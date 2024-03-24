from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
from databases.pair_database import save_to_db


class UniswapPair:
    def __init__(self, provider, factory_address, factory_abi, pool_abi, token_abi):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.factory_contract = self.w3.eth.contract(address=factory_address, abi=factory_abi)
        self.pool_abi = pool_abi
        self.token_abi = token_abi
        self.fee_tier = [500,  3000,  10000]

    def get_pool_address(self, token0_address, token1_address):
        token0_address = Web3.to_checksum_address(token0_address)
        token1_address = Web3.to_checksum_address(token1_address)
        pool_array = []
        for fee in self.fee_tier:

            try:
                pool_address = self.factory_contract.functions.getPool(token0_address, token1_address, fee).call()
                pool_contract = self.w3.eth.contract(address=pool_address, abi=self.pool_abi)
                liq = pool_contract.functions.liquidity().call()

                if pool_address is False or liq == 0:
                    continue
                else:

                    pool_array.append([self.factory_contract.functions.getPool(token0_address, token1_address, fee).call(), fee])

            except Exception as e:
                pass

        return pool_array if pool_array else -1

    def pool_exists_in_block(self, pool_address, block_number: int) -> bool:

        pool_contract = self.w3.eth.contract(address=pool_address, abi=self.pool_abi)
        try:

            pool_contract.functions.slot0().call(block_identifier=block_number)

            return True
        except BadFunctionCallOutput:
            return False

    def binary_search_pair_existence(self, token0_address, token1_address, start_block, end_block):
        token0_address = Web3.to_checksum_address(token0_address)
        token1_address = Web3.to_checksum_address(token1_address)

        if self.get_pool_address(token0_address, token1_address) == -1:
            return -1
        pools = self.get_pool_address(token0_address, token1_address)
        pair_address, _ = pools[0]
        start = start_block
        end = end_block
        while start < end:
            mid_block = (start + end) // 2
            if self.pool_exists_in_block(pair_address, mid_block):
                end = mid_block
            else:
                start = mid_block + 1
        left = start
        end = end_block
        while start < end - 1:
            mid_block = (start + end) // 2
            if self.pool_exists_in_block(pair_address, mid_block):
                start = mid_block
            else:
                end = mid_block + 1

        right = end

        return left, right if self.pool_exists_in_block(pair_address, left) and \
            self.pool_exists_in_block(pair_address, right) else -1

    def get_liquidity_from_block_range(self, token0: str, token1: str, start: int, end: int, debug=False):
        erc20_abi = self.token_abi

        debug_out = []
        token0_address = Web3.to_checksum_address(token0)
        token1_address = Web3.to_checksum_address(token1)
        pools = self.get_pool_address(token0_address, token1_address)
        print(pools)
        if pools == -1:
            return -1
        for pool in pools:

            pool_address = pool[0]
            fee = pool[1]
            pool_contract = self.w3.eth.contract(address=pool_address, abi=self.pool_abi)
            #  get decimals
            token0_contract = self.w3.eth.contract(address=token0_address, abi=erc20_abi)
            token1_contract = self.w3.eth.contract(address=token1_address, abi=erc20_abi)

            for i in range(start, end + 1):
                try:
                    slot0 = pool_contract.functions.slot0().call()
                    sqrtPriceX96 = slot0[0]

                    decimals_token0 = token0_contract.functions.decimals().call()
                    decimals_token1 = token1_contract.functions.decimals().call()

                    save_to_db(block_number=str(i),
                               token0_address=str(token0), token0_decimals=int(decimals_token0),
                               token1_address=str(token1), token1_decimals=int(decimals_token1),
                               sqrtPriceX96=str(sqrtPriceX96), fee=int(fee),
                               pool_address=str(pool_address))
                    if debug:
                        debug_out.append([sqrtPriceX96, pool_address, fee])

                except BadFunctionCallOutput:
                    return -1
        return debug_out



