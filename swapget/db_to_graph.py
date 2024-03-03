from arbitrage_utils.swapget.databases.pair_database import ReservesData
from sqlalchemy.orm import Session
import networkx as nx


def create_graph_from_db(engine, block_number: str, tokens_table: dict) -> nx.DiGraph:
    with Session(bind=engine) as session:
        result = session.query(ReservesData).filter(ReservesData.block_number == block_number)

        graph = nx.DiGraph()
        for row in result:
            token0_index = tokens_table[row.token0_address]
            token1_index = tokens_table[row.token1_address]
            weight = {'token0': row.token0_address, 'token1': row.token1_address,
                      'sqrtPrice': row.sqrtPriceX96,
                      'decimals0': row.token0_decimals, 'decimals1': row.token1_decimals,
                      'fee': row.fee,
                      'pool_address': row.pool_address}

            graph.add_edge(token0_index, token1_index, weight=weight)

    return graph
