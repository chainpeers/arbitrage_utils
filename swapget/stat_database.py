from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Chain(Base):
    __tablename__ = 'chain'

    id = Column(Integer, primary_key=True)
    chain = Column(String, unique=True, nullable=False)
    positive_changes_count = Column(Integer, default=0)
    stats = relationship("Statistic", backref="chain")


class Statistic(Base):
    __tablename__ = 'statistics'

    id = Column(Integer, primary_key=True)
    block_number = Column(Integer, nullable=False)
    change = Column(Float, nullable=False)
    base_price = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)
    token = Column(String, nullable=False)
    chain_id = Column(Integer, ForeignKey('chain.id'))


def add_chain_stat(chain: str, block_number: int, change: float, base_price: float, final_price: float, token: str):
    new_chain = session.query(Chain).filter_by(chain=chain).first()
    if not new_chain:
        new_chain = Chain(chain=chain)
        session.add(new_chain)
        session.commit()

    new_statistic = Statistic(block_number=block_number, change=change,
                              base_price=base_price, final_price=final_price, token=token, chain_id=new_chain.id)
    session.add(new_statistic)
    session.commit()

    if change > 0:
        new_chain.positive_changes_count += 1
        session.commit()



def print_chain_stats():
    chains = session.query(Chain).all()
    for chain in chains:
        print(f"Chain: {chain.chain}, Positive Changes Count: {chain.positive_changes_count}")
        statistics = session.query(Statistic).filter_by(chain_id=chain.id).all()
        for statistic in statistics:
            print(f"\tBlock Number: {statistic.block_number}, Change: {statistic.change}, "
                  f"Base Price: {statistic.base_price}, Final Price: {statistic.final_price}")


engine = create_engine('sqlite:///chainstats.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
