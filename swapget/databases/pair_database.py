from sqlalchemy import Column, String, BigInteger, create_engine, Float, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.compiler import compiles
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], ''))
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

    id = Column(SLBigInteger, primary_key=True, autoincrement=True)
    block_number = Column(Integer)
    token0_address = Column(String)
    token0_decimals = Column(Integer)
    token1_address = Column(String)
    token1_decimals = Column(Integer)
    sqrtPriceX96 = Column(String)
    fee = Column(Integer)
    pool_address = Column(String)


engine = create_engine('sqlite:///pairdata.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def save_to_db(block_number, token0_address, token0_decimals, token1_address, token1_decimals, sqrtPriceX96, fee, pool_address):
    session = Session()
    exists = session.query(session.query(ReservesData).filter_by(block_number=block_number,
                                                                 token0_address=token0_address,
                                                                 token1_address=token1_address,
                                                                 sqrtPriceX96=sqrtPriceX96,
                                                                 fee=fee).exists()).scalar()

    if not exists:
        new_data = ReservesData(
            block_number=block_number,
            token0_address=token0_address,
            token0_decimals=token0_decimals,
            token1_address=token1_address,
            token1_decimals=token1_decimals,
            sqrtPriceX96=sqrtPriceX96,
            fee=fee,
            pool_address=pool_address
        )
        session.add(new_data)
        session.commit()


def print_reserves_data():
    session = Session()
    reserves_data = session.query(ReservesData).all()
    calc = UniswapCalculator()
    for data in reserves_data:
        output_amount = calc.calculate_output_amount(data.token0_address, data.token1_address, 100, data.sqrtPriceX96,
                                                     data.token0_decimals,
                                                     data.token1_decimals, data.fee)
        print(f"ID: {data.id}, Block Number: {data.block_number}, \n"
              f"Token0 Address: {data.token0_address},\n"
              f"Token1 Address: {data.token1_address},\n"
              f"sqrtPriceX96: {data.sqrtPriceX96}, fee: {data.fee}\n"
              f"Swap_100: {output_amount}\n"
              f"Pool address: {data.pool_address}\n")


