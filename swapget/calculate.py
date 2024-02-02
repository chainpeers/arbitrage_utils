from web3 import Web3
from decimal import Decimal


class UniswapCalculator:

    def calculate_output_amount(self, input_amount, reserve1, reserve2, fee=0.003, slippage=0.01):
        # Convert to decimals for precision
        input_amount = Decimal(input_amount)
        reserve1 = Decimal(reserve1)
        reserve2 = Decimal(reserve2)
        fee = Decimal(fee)
        slippage = Decimal(slippage)

        # Calculate output amount
        # output_amount = reserve2 - (reserve1 * reserve2) / (reserve1 + input_amount) #  попытка учесть изменение пула после обмена
        # output_amount = input_amount * (reserve2 / reserve1) #  без feу и slippage
        output_amount = input_amount * ((reserve2 * (1 - fee)) / (reserve1 * (1 + slippage)))

        return float(output_amount)
