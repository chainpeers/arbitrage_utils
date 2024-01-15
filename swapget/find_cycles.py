import networkx as nx
from database import engine
from typing import List, Optional
from db_to_graph import create_graph_from_db
from calculate import UniswapCalculator

tokens_table = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 'ETH',  # ETH
                '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984': 'UNI',  # UNI
                '0x6B175474E89094C44Da98b954EedeAC495271d0F': 'DAI',  # DAI
                '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 'USDC',  # USDC
                '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2': 'MKR',  # MKR
                '0xc00e94Cb662C3520282E6f5717214004A7f2c888': 'COMP',  # COMP
                '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e': 'YFI',  # YFI
                '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9': 'AAVE',  # AAVE
                '0xB8c77482e45F1F44dE1745F52C74426C631bDD52': 'BNB',  # BNB
                '0x50327c6c5a14DCaDE707ABad2E27eB517df87AB5': 'TRON'}  # TRON


class CycleExplorer:
    def __init__(self):
        self.blocks_cycle_info = {}

    def find_cycles(self, graph: nx.DiGraph) -> Optional[List[List[str]]]:
        cycle = list(nx.simple_cycles(graph))
        return cycle

    def evaluate_cycle_for_all_tokens(self, cycle: List[str], graph, block_number):
        shifted_cycle = cycle
        for i in range(len(cycle)):
            cycle_info = self.multiply_edge_weights_of_one(graph, shifted_cycle, 100)
            shifted_cycle = shifted_cycle[-1:] + shifted_cycle[:-1]
            try:
                self.blocks_cycle_info[str(block_number)].append(cycle_info)
                print(cycle_info[str(cycle)]['change'])
            except KeyError:
                self.blocks_cycle_info[str(block_number)] = [cycle_info]

    def multiply_edge_weights_of_all(graph: nx.DiGraph, cycles: Optional[List[List[str]]], start_val: int) -> Optional[List[List]]:
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

    def multiply_edge_weights_of_one(self, graph: nx.DiGraph, cycle: Optional[List[str]], start_val: int):
        calc = UniswapCalculator()
        if cycle[0] != 'USDC':
            token_usd_edge = graph.get_edge_data(cycle[0], 'USDC')
            token_amount = calc.calculate_output_amount(start_val, token_usd_edge['weight'][1], token_usd_edge['weight'][0], fee=0)
        else:
            token_amount = start_val
        result = token_amount
        for i in range(len(cycle) - 1):
            edge_data = graph.get_edge_data(cycle[i], cycle[i + 1])
            if edge_data is not None and 'weight' in edge_data:
                result = calc.calculate_output_amount(result, edge_data['weight'][0], edge_data['weight'][1])
            else:
                raise ValueError(f"No weight found for edge between {cycle[i]} and {cycle[i + 1]}")
        result = {str(cycle): {"change": result - start_val, "token": cycle[0]}}

        return result

    def find_optimal_input_value(self, graph: nx.DiGraph, cycle: Optional[List[str]], bottom=0, top=1000, iterations=10):
        it = 0
        while it < iterations:
            middle = (bottom + top) // 2
            result_mid = self.multiply_edge_weights_of_one(graph, cycle, middle)
            result_end = self.multiply_edge_weights_of_one(graph, cycle, top)

            if result_mid[str(cycle)]["change"] > result_end[str(cycle)]["change"]:
                top = middle
            else:
                bottom = middle

            it += 1

        # Determine which of the two bounds is the optimal value
        final_result = self.multiply_edge_weights_of_one(graph, cycle, bottom)
        if final_result[str(cycle)]["change"] > result_mid[str(cycle)]["change"]:
            return [final_result, bottom]
        else:
            return [result_mid, middle]

    def gather_all_info_in_block_range(self, start, end):
        for block_number in range(start, end):
            graph = create_graph_from_db(engine, str(block_number), tokens_table)
            cycles = self.find_cycles(graph)
            for cycle in cycles:
                self.evaluate_cycle_for_all_tokens(cycle, graph, block_number)

    def find_positive_cycles_from_block_range(self, start, end):
        data = {}
        for block_number in range(start, end):
            graph = create_graph_from_db(engine, str(block_number), tokens_table)
            cycles = self.find_cycles(graph)

            for cycle in cycles:
                result, base = self.find_optimal_input_value(graph, cycle)
                if int(result[str(cycle)]["change"]) > base:
                    try:
                        data[str(cycle) + ' ' + str(base)] += 1

                    except KeyError:
                        data[str(cycle) + ' ' + str(base)] = 1
        return data

