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

    def evaluate_cycle_for_all_tokens(self, cycle: List[str], graph: nx.DiGraph, block_number: int):
        shifted_cycle = cycle
        for i in range(len(cycle)):
            cycle_info = self.multiply_edge_weights_of_one(graph, shifted_cycle, 100)
            shifted_cycle = shifted_cycle[-1:] + shifted_cycle[:-1]
            try:
                self.blocks_cycle_info[str(block_number)].append(cycle_info)
            except KeyError:
                self.blocks_cycle_info[str(block_number)] = [cycle_info]

    def multiply_edge_weights_of_all(self, graph: nx.DiGraph,
                                     cycles: Optional[List[List[str]]], start_val: int) -> Optional[List[List]]:
        data = []
        calc = UniswapCalculator()
        if not cycles:
            return None
        for vertices in cycles:
            result = start_val
            for i in range(len(vertices) - 1):
                edge_data = graph.get_edge_data(vertices[i], vertices[i + 1])
                if edge_data is not None and 'weight' in edge_data:
                    result = calc.calculate_output_amount(result, edge_data['weight'][0], edge_data['weight'][1])
                else:
                    raise ValueError(f"No weight found for edge between {vertices[i]} and {vertices[i + 1]}")
            print(result, vertices)
            data.append([result, vertices])
        return data

    def multiply_edge_weights_of_one(self, graph: nx.DiGraph, cycle: Optional[List[str]], start_val_base: int) -> dict:
        calc = UniswapCalculator()
        #  exchange for first token in cycle
        if cycle[0] != self.base_token:

            try:
                token_usd_edge = graph.get_edge_data(cycle[0], self.base_token)
                if token_usd_edge['weight'][2] == cycle[0]:
                    token_amount = calc.calculate_output_amount(start_val_base,
                                                                token_usd_edge['weight'][1],
                                                                token_usd_edge['weight'][0],
                                                                fee=0)
                else:
                    token_amount = calc.calculate_output_amount(start_val_base,
                                                                token_usd_edge['weight'][0],
                                                                token_usd_edge['weight'][1],
                                                                fee=0)
            except TypeError:
                raise TypeError(f'No weight between {cycle[0]} and {self.base_token}')

        else:
            token_amount = start_val_base

        result = token_amount
        for i in range(len(cycle)):
            # multiply all in chain
            try:
                edge_data = graph.get_edge_data(cycle[i], cycle[i + 1])
                cyc = cycle[i], cycle[i + 1]
            except IndexError:
                edge_data = graph.get_edge_data(cycle[i], cycle[0])
                cyc = cycle[i], cycle[0]
            if edge_data is not None and 'weight' in edge_data:
                if cycle[i] == edge_data['weight'][2]:
                    result = calc.calculate_output_amount(result, edge_data['weight'][0], edge_data['weight'][1])
                else:
                    result = calc.calculate_output_amount(result, edge_data['weight'][1], edge_data['weight'][0])
            else:
                raise ValueError(f"No weight found for edge between {cycle[i]} and {cycle[i + 1]}")
        #  back to base
        if cycle[0] != self.base_token:
            token_usd_edge = graph.get_edge_data(cycle[0], self.base_token)
            if token_usd_edge['weight'][2] == cycle[0]:
                result = calc.calculate_output_amount(result,
                                                            token_usd_edge['weight'][0], token_usd_edge['weight'][1],
                                                            fee=0)
            else:
                result = calc.calculate_output_amount(result,
                                                            token_usd_edge['weight'][1],
                                                            token_usd_edge['weight'][0],
                                                            fee=0)

        result = {str(cycle): {"change": result - start_val_base, "token": cycle[0], "result": result}}
        return result

    def find_optimal_input_value(self, graph: nx.DiGraph, cycle: Optional[List[str]],
                                 bottom: float = 0, top: float = 10000, iterations: int = 10) -> list[dict, float]:
        curr = 0
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

    def gather_all_info_in_block_range(self, start: int, end: int) -> None:
        for block_number in range(start, end):
            graph = create_graph_from_db(engine, str(block_number), self.token_tbl)
            cycles = self.find_cycles(graph)
            for cycle in cycles:
                self.evaluate_cycle_for_all_tokens(cycle, graph, block_number)

    def find_positive_cycles_from_block_range(self, start: int, end: int, iterations: int = 50):

        for block_number in range(start, end + 1):
            graph = create_graph_from_db(engine, str(block_number), self.token_tbl)
            cycles = self.find_cycles(graph)

            for cycle in cycles:
                result, base = self.find_optimal_input_value(graph, cycle, iterations=iterations)

                if float(result[str(cycle)]["change"]) > base:
                    add_chain_stat(str(cycle), block_number, result[str(cycle)]["change"],
                                   base, result[str(cycle)]["result"], str(cycle[0]))
        print('Chain stats saved to database')



