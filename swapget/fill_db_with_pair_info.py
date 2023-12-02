from swapget import UniswapPair
import json
from typing import List


tokens = ['0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',  # ETH
          '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',  # UNI
          '0x6B175474E89094C44Da98b954EedeAC495271d0F',  # DAI
          '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USDC
          '0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2',  # MKR
          '0xc00e94Cb662C3520282E6f5717214004A7f2c888',  # COMP
          '0x0bc529c00C6401aEF6D220BE8C6Ea1667F6Ad93e',  # YFI
          '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9']  # AAVE

provider = 'any'
factory_address = '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'
factory_abi = '[{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"}]'
with open('pairabi.json') as f:
    file_content = f.read()
    pair_abi = json.loads(file_content)


class FillDb:
    def __init__(self, provider: str, factory_address: str, factory_abi: str, pair_abi: str, start: int, end: int):
        self.uniswap = UniswapPair(provider, factory_address, factory_abi, pair_abi)
        self.start = start
        self.end = end

    def fill(self, tokens: List[str]):
        for tkn_ad1 in tokens:
            for tkn_ad2 in tokens:
                if tkn_ad1 == tkn_ad2: continue
                blocks_with_pair = self.uniswap.binary_search_pair_existence(tkn_ad1, tkn_ad2, self.start, self.end)
                if blocks_with_pair == -1:
                    print(f'The pair for {tkn_ad1} and {tkn_ad2} '
                          f'did not exist in any block between {self.start} and {self.end}')
                else:
                    self.uniswap.get_reserves_from_block_range(tkn_ad1, tkn_ad2, blocks_with_pair[0],
                                                               blocks_with_pair[1])

