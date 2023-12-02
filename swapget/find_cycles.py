import networkx as nx
from database import engine
from typing import List, Optional
from db_to_graph import create_graph_from_db

tokens_table = {'0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE': 'ETH',  # ETH
                '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984': 'UNI',  # UNI
                '0x6B175474E89094C44Da98b954EedeAC495271d0F': 'DAI',  # DAI
                '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 'USDC',  # USDC
                '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2': 'MKR',  # MKR
                '0xc00e94Cb662C3520282E6f5717214004A7f2c888': 'COMP',  # COMP
                '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e': 'YFI',  # YFI
                '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9': 'AAVE'}  # AAVE


def find_cycles(graph: nx.DiGraph) -> Optional[List[List[str]]]:
    cycle = list(nx.simple_cycles(graph))
    for c in cycle:
        c.append(c[0])
    return cycle


def multiply_edge_weights(graph: nx.DiGraph, cycles: Optional[List[List[str]]]) -> Optional[List[int]]:
    data = []
    base = 1
    if not cycles:
        return None
    for vertices in cycles:
        result = base
        for i in range(len(vertices) - 1):
            edge_data = graph.get_edge_data(vertices[i], vertices[i + 1])
            if edge_data is not None and 'weight' in edge_data:
                result *= edge_data['weight']
            else:
                raise ValueError(f"No weight found for edge between {vertices[i]} and {vertices[i + 1]}")
        data.append(result)
    return data


block_number = '18692270'
graph = create_graph_from_db(engine, block_number, tokens_table)
cycles = find_cycles(graph)
changes = multiply_edge_weights(graph, cycles)
