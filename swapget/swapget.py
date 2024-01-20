from web3 import Web3
from web3.exceptions import BadFunctionCallOutput, ContractLogicError
from database import save_to_db


class UniswapPair:
    def __init__(self, provider, factory_address, factory_abi, pair_abi, token_abi):
        self.w3 = Web3(Web3.HTTPProvider(provider))
        self.factory_contract = self.w3.eth.contract(address=factory_address, abi=factory_abi)
        self.pair_abi = pair_abi
        self.token_abi = token_abi

    def get_pair_address(self, token0_address, token1_address):
        token0_address = Web3.to_checksum_address(token0_address)
        token1_address = Web3.to_checksum_address(token1_address)

        return self.factory_contract.functions.getPair(token0_address, token1_address).call()

    def pair_exists_in_block(self, pair_address, block_number: int) -> bool:

        pair_contract = self.w3.eth.contract(address=pair_address, abi=self.pair_abi)
        try:

            pair_contract.functions.getReserves().call(block_identifier=block_number)

            return True
        except BadFunctionCallOutput:
            return False
        except ContractLogicError:
            # Если контракт вызвался, но ошибка в обработке - значит пара существует всё равно
            return True

    def binary_search_pair_existence(self, token0_address, token1_address, start_block, end_block):
        token0_address = Web3.to_checksum_address(token0_address)
        token1_address = Web3.to_checksum_address(token1_address)
        pair_address = self.get_pair_address(token0_address, token1_address)
        start = start_block
        end = end_block
        while start < end:
            mid_block = (start + end) // 2
            if self.pair_exists_in_block(pair_address, mid_block):
                end = mid_block
            else:
                start = mid_block + 1
        left = start
        end = end_block
        while start < end - 1:
            mid_block = (start + end) // 2
            if self.pair_exists_in_block(pair_address, mid_block):
                start = mid_block
            else:
                end = mid_block + 1

        right = end

        return left, right if self.pair_exists_in_block(pair_address, left) and \
            self.pair_exists_in_block(pair_address, right) else -1

    def get_reserves_from_block_range(self, token0: str, token1: str, start: int, end: int):
        erc20_abi = self.token_abi

        data = {}
        token0_address = Web3.to_checksum_address(token0)
        token1_address = Web3.to_checksum_address(token1)

        pair_address = self.get_pair_address(token0_address, token1_address)
        pair_contract = self.w3.eth.contract(address=pair_address, abi=self.pair_abi)
        for i in range(start, end + 1):
            try:

                #  get decimals
                token0_contract = self.w3.eth.contract(address=token0_address, abi=erc20_abi)
                token1_contract = self.w3.eth.contract(address=token1_address, abi=erc20_abi)

                decimals_token0 = token0_contract.functions.decimals().call()

                decimals_token1 = token1_contract.functions.decimals().call()

                data[i] = pair_contract.functions.getReserves().call(block_identifier=i)
                #  pair has one order always. need to check who is who
                if decimals_token0 == pair_contract.functions.decimals().call():
                    data[i][0] = data[i][0] / (10 ** decimals_token0)
                    data[i][1] = data[i][1] / (10 ** decimals_token1)
                else:
                    data[i][1] = data[i][1] / (10 ** decimals_token0)
                    data[i][0] = data[i][0] / (10 ** decimals_token1)

                save_to_db(int(i), str(token0), str(data[i][0]), str(token1), str(data[i][1]))
            except BadFunctionCallOutput:
                return -1
        return data


