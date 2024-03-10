from find_cycles import CycleExplorer
import json
from fill_db_with_pair_info import FillDb
from arbitrage_utils.swapget.databases.stat_database import print_chain_stats
from arbitrage_utils.swapget.databases.pair_database import print_reserves_data
from web3 import Web3


with open('token_table.json') as f:
    file_content = f.read()
    TOKENS_TBL = json.loads(file_content)

with open('settings.json') as f:
    file_content = f.read()
    provider = json.loads(file_content)[0]['provider']
    factory_address = json.loads(file_content)[0]['factory_address']

# ABI распаковка
with open('abi/pair_abi.json') as f:
    file_content = f.read()
    pair_abi = json.loads(file_content)

with open('abi/token_abi.json') as f:
    file_content = f.read()
    token_abi = json.loads(file_content)

with open('abi/factory_abi.json') as f:
    file_content = f.read()
    factory_abi = json.loads(file_content)


web3 = Web3(Web3.HTTPProvider(provider))
last = web3.eth.block_number

db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, last-1, last)

db_filler.fill(TOKENS_TBL)

print_reserves_data()

cycleexp = CycleExplorer(TOKENS_TBL)

cycleexp.find_positive_cycles_from_block_range(19356670, 19356671, 3)


print_chain_stats()




