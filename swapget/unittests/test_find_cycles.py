import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from find_cycles import CycleExplorer
import networkx as nx
from calculate import UniswapCalculator
import json


base_dir = os.path.dirname(os.path.abspath(__file__))
uniswap_pool_abi_path = os.path.join(base_dir, '..', 'abi')


class TestCycleExplorer(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(uniswap_pool_abi_path, 'token_abi.json')) as f:
            file_content = f.read()
            self.TOKENS_TBL = json.loads(file_content)

        self.instance = CycleExplorer(self.TOKENS_TBL)
        self.token0 = 'token0'
        self.token1 = 'token1'
        self.val = 1000
        self.calc = UniswapCalculator()
        self.graph = nx.DiGraph()

    def test_swap_token(self):
        edge_token = False
        pool_array = []
        # Мокируем методы get_edge_data и calculate_output_amount
        with patch('networkx.DiGraph.get_edge_data', return_value={
            'weight': {'token0': 'token0', 'token1': 'token1', 'sqrtPrice': 1000, 'decimals0': 18, 'decimals1': 18,
                       'pool_address': 'pool_address', 'fee': 0.03}}) as mock_get_edge_data:
            with patch.object(self.calc, 'calculate_output_amount', return_value=100) as mock_calculate_output_amount:
                result = self.instance._swap_token(self.token0, self.token1, self.val, self.calc, self.graph, pool_array, edge_token)

                # Проверяем, что get_edge_data был вызван с правильными аргументами
                mock_get_edge_data.assert_called_once_with(self.token0, self.token1)

                # Проверяем, что calculate_output_amount был вызван с правильными аргументами
                mock_calculate_output_amount.assert_called_once_with(input_amount=self.val,
                                                                     token0=self.token0,
                                                                     token1=self.token1,
                                                                     sqrtPriceX96=1000,
                                                                     token0_decimals=18,
                                                                     token1_decimals=18,
                                                                     fee=0)

                # Проверяем, что pool_array был изменен правильно
                self.assertEqual(pool_array, [{'pool_address': 0.03}])

                # Проверяем, что функция возвращает ожидаемое значение
                self.assertEqual(result, 100)

    def test_swap_token_edge(self):
        edge_token = True
        pool_array = []
        # Мокируем методы get_edge_data и calculate_output_amount
        with patch('networkx.DiGraph.get_edge_data', return_value={
            'weight': {'token0': 'token0', 'token1': 'token1', 'sqrtPrice': 1000, 'decimals0': 18, 'decimals1': 18,
                       'pool_address': 'pool_address', 'fee': 0.03}}) as mock_get_edge_data:
            with patch.object(self.calc, 'calculate_output_amount', return_value=100) as mock_calculate_output_amount:
                result = self.instance._swap_token(self.token0, self.token1, self.val, self.calc, self.graph,
                                                   pool_array, edge_token)

                # Проверяем, что get_edge_data был вызван с правильными аргументами
                mock_get_edge_data.assert_called_once_with(self.token0, self.token1)

                # Проверяем, что calculate_output_amount был вызван с правильными аргументами
                mock_calculate_output_amount.assert_called_once_with(input_amount=self.val,
                                                                     token0=self.token0,
                                                                     token1=self.token1,
                                                                     sqrtPriceX96=1000,
                                                                     token0_decimals=18,
                                                                     token1_decimals=18,
                                                                     fee=0)

                # Проверяем, что pool_array был изменен правильно
                self.assertEqual(pool_array, [{'pool_address': 'base 0'}])

                # Проверяем, что функция возвращает ожидаемое значение
                self.assertEqual(result, 100)

    def test_swap_token_no_weight(self):
        edge_token = False
        pool_array = []
        # Мокируем методы get_edge_data и calculate_output_amount
        with patch('networkx.DiGraph.get_edge_data', side_effect=TypeError("No weight found")) as mock_get_edge_data:
            with patch.object(self.calc, 'calculate_output_amount', return_value=100) as mock_calculate_output_amount:
                result = self.instance._swap_token(self.token0, self.token1, self.val, self.calc, self.graph,
                                                   pool_array, edge_token)

                # Проверяем, что get_edge_data был вызван с правильными аргументами
                mock_get_edge_data.assert_called_once_with(self.token0, self.token1)

                # Проверяем, что calculate_output_amount не вызывалась
                mock_calculate_output_amount.assert_not_called()

                # Проверяем, что pool_array не тронуло
                self.assertEqual(pool_array, [])

                # Проверяем, что функция возвращает -1 как сигнал проблемы
                self.assertEqual(result, -1)

    def test_multiply_edge_weights_of_one_not_starting_with_base(self):
        instance = CycleExplorer(self.TOKENS_TBL, base_token='token0')
        graph = nx.DiGraph()
        cycle = ['token1', 'token2', 'token3']
        start_val_base = 1000

        with patch.object(CycleExplorer, '_swap_token', return_value=100) as mock_swap_token:
            result = instance.multiply_edge_weights_of_one(graph, cycle, start_val_base)

        self.assertEqual(result, {"['token1', 'token2', 'token3']":
                                  {'change': -900,
                                   'token': 'token1',
                                   'result': 100,
                                   'pool_array': []}})

        self.assertEqual(mock_swap_token.call_count, len(cycle)+2)

    def test_multiply_edge_weights_of_one_starting_with_base(self):
        instance = CycleExplorer(self.TOKENS_TBL, base_token='token0')
        graph = nx.DiGraph()
        cycle = ['token0', 'token1', 'token2']
        start_val_base = 1000

        with patch.object(CycleExplorer, '_swap_token', return_value=100) as mock_swap_token:
            result = instance.multiply_edge_weights_of_one(graph, cycle, start_val_base)
        self.assertEqual(result, {"['token0', 'token1', 'token2']":
                                  {'change': -900,
                                   'token': 'token0',
                                   'result': 100,
                                   'pool_array': []}})
        mock_swap_token.assert_called()
        self.assertEqual(mock_swap_token.call_count, len(cycle))

    def test_multiply_edge_weights_of_one_empty_cycle(self):
        instance = CycleExplorer(self.TOKENS_TBL, base_token='token0')
        graph = nx.DiGraph()
        cycle = []
        start_val_base = 1000

        with patch.object(CycleExplorer, '_swap_token', return_value=100) as mock_swap_token:
            result = instance.multiply_edge_weights_of_one(graph, cycle, start_val_base)

        self.assertIsNone(result)
        mock_swap_token.assert_not_called()

    def test_find_optimal_input_value(self):

        instance = CycleExplorer(self.TOKENS_TBL)
        cycle = ['A', 'B', 'C', 'A']

        with patch.object(CycleExplorer, 'multiply_edge_weights_of_one',
                          return_value={str(cycle): {'change': 10}}) as mock_multiply_edge_weights_of_one:
            graph = nx.DiGraph()
            result = instance.find_optimal_input_value(graph, cycle, iterations=2)
            expected_calls = [
                unittest.mock.call(graph, cycle, 5000),
                unittest.mock.call(graph, cycle, 10000),
                unittest.mock.call(graph, cycle, 7500),
                unittest.mock.call(graph, cycle, 10000),
                unittest.mock.call(graph, cycle, 7500)
            ]
            mock_multiply_edge_weights_of_one.assert_has_calls(expected_calls)

            expected_result = [{str(cycle): {'change': 10}}, 7500]
            self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
