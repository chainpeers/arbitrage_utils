from sqlalchemy import Column, String, BigInteger, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.compiler import compiles
from calculate import UniswapCalculator

Base = declarative_base()


class SLBigInteger(BigInteger):
    pass


@compiles(SLBigInteger, 'sqlite')
def bi_c(element, compiler, **kw):
    return "INTEGER"


@compiles(SLBigInteger)
def bi_c(element, compiler, **kw):
    return compiler.visit_BIGINT(element, **kw)


class ReservesData(Base):
    __tablename__ = 'uniswappairs'

    id = Column(SLBigInteger(), primary_key=True)
    block_number = Column(String)
    token0_address = Column(String)
    token0_reserve = Column(String)
    token1_address = Column(String)
    token1_reserve = Column(String)


engine = create_engine('sqlite:///pairdata.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def save_to_db(block_number, token0_address, token0_reserve, token1_address, token1_reserve):
    session = Session()
    exists = session.query(session.query(ReservesData).filter_by(block_number=block_number,
                                                                 token0_address=token0_address,
                                                                 token0_reserve=token0_reserve,
                                                                 token1_address=token1_address,
                                                                 token1_reserve=token1_reserve).exists()).scalar()
    if not exists:
        new_data = ReservesData(
            block_number=block_number,
            token0_address=token0_address,
            token0_reserve=token0_reserve,
            token1_address=token1_address,
            token1_reserve=token1_reserve
        )
        session.add(new_data)
        session.commit()


def print_reserves_data():
    session = Session()
    reserves_data = session.query(ReservesData).all()
    calc = UniswapCalculator()
    for data in reserves_data:
        print(f"ID: {data.id}, Block Number: {data.block_number}, "
              f"Token0 Address: {data.token0_address}, Token0 Reserve: {data.token0_reserve}, "
              f"Token1 Address: {data.token1_address}, Token1 Reserve: {data.token1_reserve}, "
              f"Swap_100: {calc.calculate_output_amount(100, data.token0_reserve, data.token1_reserve)}")


