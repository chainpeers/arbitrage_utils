import networkx as nx
from database import engine
from typing import List, Optional
from db_to_graph import create_graph_from_db
from calculate import UniswapCalculator
from stat_database import add_chain_stat


class CycleExplorer:
    def __init__(self, token_tbl, base_token: str = "USDC"):
        self.blocks_cycle_info = {}
        self.token_tbl = token_tbl
        self.base_token = base_token

    def find_cycles(self, graph: nx.DiGraph) -> Optional[List[List[str]]]:
        cycle = list(nx.simple_cycles(graph))
        return cycle

    def multiply_edge_weights_of_one(self, graph: nx.DiGraph, cycle: Optional[List[str]], start_val_base: int) -> dict:
        calc = UniswapCalculator()
        pool_array = []
        fee_array = []
        #  exchange for first token in cycle
        if cycle[0] != self.base_token:

            try:
                token_usd_edge = graph.get_edge_data(self.base_token, cycle[0])

                token_amount = calc.calculate_output_amount(input_amount=start_val_base,
                                                            token0=token_usd_edge['weight']['token0'],
                                                            token1=token_usd_edge['weight']['token1'],
                                                            sqrtPriceX96=token_usd_edge['weight']['sqrtPrice'],
                                                            token0_decimals=token_usd_edge['weight']['decimals0'],
                                                            token1_decimals=token_usd_edge['weight']['decimals1'],
                                                            fee=0)
                pool_array.append(token_usd_edge['weight']['pool_address'])
                fee_array.append('base 0')
            except TypeError:
                print(f'No weight between {cycle[0]} and {self.base_token}')
                return -1

        else:
            token_amount = start_val_base

        result = token_amount
        for i in range(len(cycle)):
            # multiply all in chain
            try:
                edge_data = graph.get_edge_data(cycle[i], cycle[i + 1])
            except IndexError:
                edge_data = graph.get_edge_data(cycle[i], cycle[0])
            if edge_data is not None and 'weight' in edge_data:

                result = calc.calculate_output_amount(input_amount=result, token0=edge_data['weight']['token0'],
                                                      token1=edge_data['weight']['token1'],
                                                      sqrtPriceX96=edge_data['weight']['sqrtPrice'],
                                                      token0_decimals=edge_data['weight']['decimals0'],
                                                      token1_decimals=edge_data['weight']['decimals1'],
                                                      fee=edge_data['weight']['fee'])
                pool_array.append(edge_data['weight']['pool_address'])
                fee_array.append(edge_data['weight']['fee'])

            else:
                raise ValueError(f"No weight found for edge between {cycle[i]} and {cycle[i + 1]}")
        #  back to base
        if cycle[0] != self.base_token:
            token_usd_edge = graph.get_edge_data(cycle[0], self.base_token)

            result = calc.calculate_output_amount(input_amount=result, token0=token_usd_edge['weight']['token0'],
                                                  token1=token_usd_edge['weight']['token1'],
                                                  sqrtPriceX96=token_usd_edge['weight']['sqrtPrice'],
                                                  token0_decimals=token_usd_edge['weight']['decimals0'],
                                                  token1_decimals=token_usd_edge['weight']['decimals1'],
                                                  fee=0)
            pool_array.append(token_usd_edge['weight']['pool_address'])
            fee_array.append('base 0')
        result = {str(cycle): {"change": result - start_val_base, "token": cycle[0], "result": result,
                               "pool_array":pool_array, 'fee_array': fee_array}}
        return result

    def find_optimal_input_value(self, graph: nx.DiGraph, cycle: Optional[List[str]],
                                 bottom: float = 0, top: float = 10000, iterations: int = 10) -> list:

        curr = 0
        while curr < iterations:
            middle = (bottom + top) // 2
            result_mid = self.multiply_edge_weights_of_one(graph, cycle, middle)
            if result_mid == -1:
                return [-1, -1]
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
                if result == -1:
                    continue

                if float(result[str(cycle)]["change"]) > base:
                    add_chain_stat(str(cycle), block_number, result[str(cycle)]["change"],
                                   base, result[str(cycle)]["result"], str(cycle[0]), str(result[str(cycle)]["fee_array"]),
                                   str(result[str(cycle)]["pool_array"]))
        print('Chain stats saved to database')



