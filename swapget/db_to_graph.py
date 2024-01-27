from database import ReservesData
from sqlalchemy.orm import Session
import networkx as nx


def create_graph_from_db(engine, block_number: str, tokens_table: dict) -> nx.DiGraph:
    with Session(bind=engine) as session:
        result = session.query(ReservesData).filter(ReservesData.block_number == block_number)

        graph = nx.DiGraph()
        for row in result:
            token0_index = tokens_table[row.token0_address]
            token1_index = tokens_table[row.token1_address]
            weight = [float(row.token0_reserve), float(row.token1_reserve)]

            graph.add_edge(token0_index, token1_index, weight=weight)

    return graph
