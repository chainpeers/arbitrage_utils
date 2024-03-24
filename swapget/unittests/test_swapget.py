import unittest
import json
import sys
import os
sys.path.insert(2, os.path.join(sys.path[0], '..'))
from swapget import UniswapPair
from unittest.mock import patch, MagicMock
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput


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

    @patch('web3.Web3.to_checksum_address')
    def test_get_pool_address_is_correct(self, mock_to_checksum_address):
        uni_instance = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        uni_instance.factory_contract = MagicMock()
        uni_instance.factory_contract.functions.getPool.return_value = MagicMock()
        uni_instance.factory_contract.functions.getPool.return_value.call.return_value = 'test'

        mock_to_checksum_address.to_checksum_address.return_value = '0xToken123'

        uni_instance.w3 = MagicMock()
        uni_instance.w3.eth.contract.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.liquidity.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.liquidity.return_value.call.return_value = 'test2'

        result = uni_instance.get_pool_address('0xToken0', '0xToken1')

        expected_result = [
            ['test', 500],
            ['test', 3000],
            ['test', 10000]
        ]
        self.assertEqual(uni_instance.factory_contract.functions.getPool.call_count,
                         len(uni_instance.fee_tier) * 2)
        self.assertEqual(uni_instance.w3.eth.contract.return_value.functions.liquidity.call_count,
                         len(uni_instance.fee_tier))
        self.assertEqual(result, expected_result)

    @patch('web3.Web3.to_checksum_address')
    def test_get_pool_address_is_wrong(self, mock_to_checksum_address):
        uni_instance = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        uni_instance.factory_contract = MagicMock()
        uni_instance.factory_contract.functions.getPool.return_value = MagicMock()
        uni_instance.factory_contract.functions.getPool.return_value.call.side_effect = TypeError()

        mock_to_checksum_address.to_checksum_address.return_value = '0xToken123'

        uni_instance.w3 = MagicMock()
        uni_instance.w3.eth.contract.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.liquidity.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.liquidity.return_value.call.return_value = 'test2'

        result = uni_instance.get_pool_address('0xToken0', '0xToken1')

        expected_result = -1
        self.assertEqual(uni_instance.factory_contract.functions.getPool.call_count,
                         3)
        self.assertEqual(uni_instance.w3.eth.contract.return_value.functions.liquidity.call_count,
                         0)
        self.assertEqual(result, expected_result)

    def test_pool_exists_in_block_and_it_is_true(self):
        uni_instance = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        uni_instance.w3 = MagicMock()
        uni_instance.w3.eth.contract.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value.call.return_value = 'ok'

        result = uni_instance.pool_exists_in_block('123', 123)
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value.call.called_once_with(123)
        self.assertEqual(result, True)

    def test_pool_exists_in_block_and_it_is_false(self):
        uni_instance = UniswapPair(self.provider, self.factory_address, self.factory_abi, self.pair_abi, self.token_abi)
        uni_instance.w3 = MagicMock()
        uni_instance.w3.eth.contract.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value = MagicMock()
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value.call.side_effect = BadFunctionCallOutput()

        result = uni_instance.pool_exists_in_block('123', 123)
        uni_instance.w3.eth.contract.return_value.functions.slot0.return_value.call.called_once_with(123)
        self.assertEqual(result, False)


if __name__ == '__main__':
    unittest.main()
