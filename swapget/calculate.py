from decimal import Decimal, getcontext


class UniswapCalculator:

    def calculate_output_amount(self, token0, token1, input_amount,
                                sqrtPriceX96, token0_decimals, token1_decimals, fee=3000):
        # Set the precision for Decimal calculations
        input_amount = Decimal(input_amount)
        getcontext().prec = 10

        # Convert sqrtPriceX96 from Q96 format to a normal decimal
        price_ratio = Decimal(sqrtPriceX96) / Decimal(2 ** 96)
        price_ratio = price_ratio ** 2

        if token0 < token1:
            price_ratio = price_ratio / Decimal(10 ** (token1_decimals - token0_decimals))
            fee_decimal = Decimal(fee) / 1000000
            output_amount = input_amount * price_ratio * (1 - fee_decimal)
        else:
            price_ratio = price_ratio / Decimal(10 ** (token0_decimals - token1_decimals))
            fee_decimal = Decimal(fee) / 1000000
            output_amount = input_amount / price_ratio * (1 - fee_decimal)

        return output_amount
