from find_cycles import CycleExplorer
import json
from fill_db_with_pair_info import FillDb
from databases.stat_database import print_chain_stats
from databases.pair_database import print_reserves_data



with open('token_table.json') as f:
    file_content = f.read()
    TOKENS_TBL = json.loads(file_content)

with open('settings.json') as f:
    file_content = f.read()
    provider = json.loads(file_content)[0]['provider']
    factory_address = json.loads(file_content)[0]['factory_address']

# ABI распаковка
with open('abi/UniswapV3Pool.json') as f:
    file_content = f.read()
    pair_abi = json.loads(file_content)

with open('abi/token_abi.json') as f:
    file_content = f.read()
    token_abi = json.loads(file_content)

with open('abi/UniswapV3Factory.json') as f:
    file_content = f.read()
    factory_abi = json.loads(file_content)


# web3 = Web3(Web3.HTTPProvider(provider))
# last = web3.eth.block_number
#
db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, 19506068, 19506069)

db_filler.fill(TOKENS_TBL)

print_reserves_data()

cycleexp = CycleExplorer(TOKENS_TBL)

cycleexp.find_positive_cycles_from_block_range(19506068, 19506069, 10)

print_chain_stats()




