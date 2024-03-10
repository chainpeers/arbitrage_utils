import unittest
import json
from arbitrage_utils.swapget.swapget import UniswapPair
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
uniswap_pool_abi_path = os.path.join(base_dir, '..', 'abi')


class TestUniswapPair(unittest.TestCase):
    def setUp(self):
        self.provider = 'https://mainnet.infura.io/v3/5d89fce7f6d74f5e9807b50a60b02e0a'
        self.factory_address = '0x1F98431c8aD98523631AE4a59f267346ea31F984'

        with open(os.path.join(uniswap_pool_abi_path, 'UniswapV3Pool.json')) as f:
            file_content = f.read()
            self.pair_abi = json.loads(file_content)

        with open(os.path.join(uniswap_pool_abi_path, 'token_abi.json')) as f:
            file_content = f.read()
            self.token_abi = json.loads(file_content)

        with open(os.path.join(uniswap_pool_abi_path, 'UniswapV3Factory.json')) as f:
            file_content = f.read()
            self.factory_abi = json.loads(file_content)

    def test_get_pool_address(self):
        uniswap = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        get_address_call = uniswap.get_pool_address(0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984,
                                                    0x6B175474E89094C44Da98b954EedeAC495271d0F)
        self.assertEqual(get_address_call, [['0x57D7d040438730d4029794799dEEd8601E23fF80', 500],
                                            ['0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 3000],
                                            ['0xD6993E525FAdB23971a20bBb057Af9841eAE076F', 10000]])
        get_address_call = uniswap.get_pool_address(0x1f9840a8515aF5bf1D1761F925BDADdC4201F984,
                                                    0x6B175474E89094C44Da925954EedeAC495271d0F)
        self.assertEqual(get_address_call, -1)
        get_address_call = uniswap.get_pool_address(0x6B175474E89094C44Da98b954EedeAC495271d0F,
                                                    0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984)
        self.assertEqual(get_address_call, [['0x57D7d040438730d4029794799dEEd8601E23fF80', 500],
                                            ['0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 3000],
                                            ['0xD6993E525FAdB23971a20bBb057Af9841eAE076F', 10000]])

    def test_pool_exists_in_block(self):
        uniswap = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        get_exists_call = uniswap.pool_exists_in_block('0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 0)
        self.assertEqual(get_exists_call, False)
        get_exists_call = uniswap.pool_exists_in_block('0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 19000000)
        self.assertEqual(get_exists_call, True)

    def test_binary_search_pair_existence(self):
        uniswap = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        bi_search_call = uniswap.binary_search_pair_existence(0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984,
                                                              0x6B175474E89094C44Da98b954EedeAC495271d0F,
                                                              10000000, 19000005)
        self.assertEqual(bi_search_call, (12383330, 19000005))
        bi_search_call = uniswap.binary_search_pair_existence(0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984,
                                                              0x6B175474E89094C44Da98b954EedeAC495271d0F,
                                                              19000000, 19000005)

        self.assertEqual(bi_search_call, (19000000, 19000005))

    def test_get_liquidity_from_block_range(self):
        uniswap = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        get_liq_good_call = uniswap.get_liquidity_from_block_range('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                                                                   '0x6B175474E89094C44Da98b954EedeAC495271d0F',
                                                                   19000005, 19000006, debug=True)
        self.assertEqual(get_liq_good_call, [[2226807304819451294225431920,
                                              '0x57D7d040438730d4029794799dEEd8601E23fF80', 500],
                                             [2226807304819451294225431920,
                                              '0x57D7d040438730d4029794799dEEd8601E23fF80', 500],
                                             [311304595491026851434048245117,
                                              '0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 3000],
                                             [311304595491026851434048245117,
                                              '0x7cf70eD6213F08b70316bD80F7c2ddDc94E41aC5', 3000],
                                             [240909345684574701522037830932,
                                              '0xD6993E525FAdB23971a20bBb057Af9841eAE076F', 10000],
                                             [240909345684574701522037830932,
                                              '0xD6993E525FAdB23971a20bBb057Af9841eAE076F', 10000]])

        get_liq_bad_call = uniswap.get_liquidity_from_block_range('0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
                                                                  '0x6B175474E89094C44Da98b954EedeAC495271d0a',
                                                                  19000005, 19000006, debug=True)
        self.assertEqual(get_liq_bad_call, -1)
if __name__ == '__main__':
    unittest.main()
