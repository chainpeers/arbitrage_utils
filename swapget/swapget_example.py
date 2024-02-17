from find_cycles import CycleExplorer
import json
from fill_db_with_pair_info import FillDb
from stat_database import print_chain_stats
from database import print_reserves_data
from calculate import UniswapCalculator
from web3 import Web3

TOKENS_TBL = {
                '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984': 'UNI',  # UNI
                '0x6b175474e89094c44da98b954eedeac495271d0f': 'DAI',  # DAI
                '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48': 'USDC',  # USDC
                '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2': 'MKR',  # MKR
                '0xc00e94Cb662C3520282E6f5717214004A7f2c888': 'COMP',  # COMP
                '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e': 'YFI',  # YFI
                '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9': 'AAVE',  # AAVE
                '0xB8c77482e45F1F44dE1745F52C74426C631bDD52': 'BNB',  # BNB
                '0x50327c6c5a14DCaDE707ABad2E27eB517df87AB5': 'TRON',
                '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2': 'WETH'}  # TRON

provider = 'Your Infura Provider'

# Адрес контракта Uniswap
factory_address = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

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
# # #
# db_filler = FillDb(provider, factory_address, factory_abi, pair_abi, token_abi, last-1, last)
# db_filler.fill(TOKENS_TBL)

# print_reserves_data()

# cycleexp = CycleExplorer(TOKENS_TBL)
#
# cycleexp.find_positive_cycles_from_block_range(19243615, 19243616, 3)
#
print_chain_stats()




