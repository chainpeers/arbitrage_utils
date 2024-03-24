import networkx as nx
from typing import List, Optional
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from databases.pair_database import engine
from db_to_graph import create_graph_from_db
from calculate import UniswapCalculator
from databases.stat_database import add_chain_stat


class CycleExplorer:
    def __init__(self, token_tbl, base_token: str = "USDC"):
        self.token_tbl = token_tbl
        self.base_token = base_token

    def find_cycles(self, graph: nx.DiGraph) -> Optional[List[List[str]]]:
        cycle = list(nx.simple_cycles(graph))
        return cycle

    def _swap_token(self, token0, token1, val, calc, graph, pool_array, edge_token=False):
        try:
            token_edge = graph.get_edge_data(token0, token1)
            token_amount = calc.calculate_output_amount(input_amount=val,
                                                        token0=token_edge['weight']['token0'],
                                                        token1=token_edge['weight']['token1'],
                                                        sqrtPriceX96=token_edge['weight']['sqrtPrice'],
                                                        token0_decimals=token_edge['weight']['decimals0'],
                                                        token1_decimals=token_edge['weight']['decimals1'],
                                                        fee=0)
            if edge_token:
                pool_array.append({token_edge['weight']['pool_address']: 'base 0'})
            else:
                pool_array.append({token_edge['weight']['pool_address']: token_edge['weight']['fee']})
        except TypeError:
            print(f'No weight between {token0} and {token1}')
            return -1

        return token_amount

    def multiply_edge_weights_of_one(self, graph: nx.DiGraph, cycle: Optional[List[str]],
                                     start_val_base: int) -> Optional[dict]:
        if not cycle:
            return None
        calc = UniswapCalculator()
        pool_array = []
        first_not_base = cycle[0] != self.base_token

        #  swap from base
        if first_not_base:
            result = self._swap_token(self.base_token, cycle[0],
                                      val=start_val_base, calc=calc, graph=graph, pool_array=pool_array,
                                      edge_token=True)
        else:
            result = start_val_base
        #  count chain results
        for i in range(len(cycle)):

            if i < len(cycle) - 1:
                result = self._swap_token(cycle[i], cycle[i+1],
                                          val=result, calc=calc, graph=graph, pool_array=pool_array)
            else:
                result = self._swap_token(cycle[i], cycle[0],
                                          val=result, calc=calc, graph=graph, pool_array=pool_array)

        #  back to base
        if first_not_base:
            result = self._swap_token(cycle[0], self.base_token,
                                      val=result, calc=calc, graph=graph, pool_array=pool_array,
                                      edge_token=True)

        result = {str(cycle): {"change": result - start_val_base,
                               "token": cycle[0],
                               "result": result,
                               "pool_array": pool_array}}
        return result

    def find_optimal_input_value(self, graph: nx.DiGraph, cycle: Optional[List[str]],
                                 bottom: float = 0, top: float = 10000, iterations: int = 10) -> list[dict, float]:
        curr = 0
        middle = 0
        result_mid = 0
        while curr < iterations:
            middle = (bottom + top) // 2
            result_mid = self.multiply_edge_weights_of_one(graph, cycle, middle)
            result_end = self.multiply_edge_weights_of_one(graph, cycle, top)

            if result_mid[str(cycle)]["change"] > result_end[str(cycle)]["change"]:
                top = middle
            else:
                bottom = middle

            curr += 1

        final_result = self.multiply_edge_weights_of_one(graph, cycle, middle)
        if final_result[str(cycle)]["change"] > result_mid[str(cycle)]["change"]:
            return [final_result, bottom]
        else:
            return [result_mid, middle]

    def find_positive_cycles_from_block_range(self, start: int, end: int, iterations: int = 50):

        for block_number in range(start, end + 1):
            graph = create_graph_from_db(engine, str(block_number), self.token_tbl)
            cycles = self.find_cycles(graph)

            for cycle in cycles:
                result, base = self.find_optimal_input_value(graph, cycle, iterations=iterations)
                # print(result)
                if float(result[str(cycle)]["change"]) > 0:
                    add_chain_stat(str(cycle), block_number, result[str(cycle)]["change"],

                                   base, result[str(cycle)]["result"], str(cycle[0]),
                                   str(result[str(cycle)]["pool_array"]))

        print('Chain stats saved to database')



