from swapget import UniswapPair


class FillDb:
    def __init__(self, provider: str, factory_address: str, factory_abi: str, pair_abi: str, token_abi: str,
                 start: int, end: int):
        self.uniswap = UniswapPair(provider, factory_address, factory_abi, pair_abi, token_abi)
        self.start = start
        self.end = end

    def fill(self, tokens: dict) -> None:
        tokens = list(tokens.keys())
        for tkn_ad1 in tokens:
            for tkn_ad2 in tokens:
                if tkn_ad1 == tkn_ad2:
                    continue
                blocks_with_pair = self.uniswap.binary_search_pair_existence(tkn_ad1, tkn_ad2, self.start, self.end)
                if blocks_with_pair == -1:
                    pass
                else:
                    self.uniswap.get_liquidity_from_block_range(tkn_ad1, tkn_ad2, blocks_with_pair[0],
                                                                blocks_with_pair[1])
