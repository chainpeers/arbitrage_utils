from web3 import Web3
from decimal import Decimal


class UniswapCalculator:

    def calculate_output_amount(self, input_amount, reserve1, reserve2, fee=0.003):

        # Convert to decimals for precision
        input_amount = Decimal(input_amount)
        reserve1 = Decimal(reserve1)
        reserve2 = Decimal(reserve2)

        # Calculate output amount
        output_amount = reserve2 - (reserve1 * reserve2) / (reserve1 + input_amount)

        # Apply Uniswap's 0.3% fee
        output_amount = output_amount * Decimal(1 - fee)

        return float(output_amount)

