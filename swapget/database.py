from sqlalchemy import Column, String, BigInteger, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.compiler import compiles
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
    __tablename__ = 'reserves'

    id = Column(SLBigInteger(), primary_key=True)
    block_number = Column(String)
    token0_address = Column(String)
    token0_reserve = Column(String)
    token1_address = Column(String)
    token1_reserve = Column(String)


engine = create_engine('sqlite:///mydatabase.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


def save_to_db(block_number, token0_address, token0_reserve, token1_address, token1_reserve):
    session = Session()
    new_data = ReservesData(
        block_number=block_number,
        token0_address=token0_address,
        token0_reserve=token0_reserve,
        token1_address=token1_address,
        token1_reserve=token1_reserve
    )
    session.add(new_data)
    session.commit()
