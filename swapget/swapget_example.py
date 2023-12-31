from swapget import UniswapPair
from sqlalchemy.orm import Session
from database import ReservesData, engine
from find_cycles import CycleExplorer
import json

provider = 'Your Provider'

# Адрес контракта Uniswap
factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
# ABI контракта Factory
factory_abi = '[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'

# ABI контракта Pair
with open('pairabi.json') as f:
    file_content = f.read()
    pair_abi = json.loads(file_content)

uniswap = UniswapPair(provider, factory_address, factory_abi, pair_abi)

# Адреса двух токенов
token0_address = '0x7825e833d495f3d1c28872415a4aee339d26ac88'
token1_address = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'

# Начальный и конечный блоки для поиска
start_block = uniswap.w3.eth.block_number - 10
end_block = uniswap.w3.eth.block_number
print(start_block)
# Получение диапазона пары в отрезке блоков
blocks_with_pair = uniswap.binary_search_pair_existence(token0_address, token1_address, start_block, end_block)

if blocks_with_pair == -1:
    print(f'The pair did not exist in any block between {start_block} and {end_block}')

else:

    print(f'The pair first existed in blocks from {blocks_with_pair[0]} to {blocks_with_pair[1]}')
    # Получения всех резервов диапазона
    uniswap.get_reserves_from_block_range(token0_address,token1_address,blocks_with_pair[0], blocks_with_pair[1])
    # Создаем сессию
    session = Session(bind=engine)

    # Получаем все записи из таблицы ReservesData
    reserves_data = session.query(ReservesData).all()

    # Выводим все записи
    for data in reserves_data:
        print(vars(data))

    # Закрываем сессию
    session.close()

cycleexp = CycleExplorer()
data = cycleexp.find_positive_cycles_from_block_range(18748900, 18749109)
print(len(data))
for i, k in data.items():

    print(i, k)