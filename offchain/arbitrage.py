class ArbitrageFinder:
    def __init__(self, dex_clients, config):
        self.dex_clients = dex_clients
        self.config = config

    def find_2way_arbitrage(self, prices, liquidity, min_profit=1.0):
        results = []
        for buy_dex in prices:
            for sell_dex in prices:
                if buy_dex == sell_dex:
                    continue
                for pair in prices[buy_dex]:
                    if pair in prices[sell_dex]:
                        buy_price = prices[buy_dex][pair]
                        sell_price = prices[sell_dex][pair]
                        spread = sell_price - buy_price
                        liq_buy = liquidity.get(buy_dex, {}).get(pair, 0)
                        liq_sell = liquidity.get(sell_dex, {}).get(pair, 0)
                        slippage = 0  # Можно доработать расчёт
                        fee_total = buy_price * self.config.dex_fees.get(buy_dex, 0.0025) + \
                                    sell_price * self.config.dex_fees.get(sell_dex, 0.0025) + \
                                    buy_price * self.config.flash_loan_fee
                        profit = spread - fee_total
                        result = {
                            'pair': pair,
                            'buy_on': buy_dex,
                            'sell_on': sell_dex,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'spread': spread,
                            'liq_buy': liq_buy,
                            'liq_sell': liq_sell,
                            'slippage': slippage,
                            'fee_total': fee_total,
                            'profit': profit
                        }
                        if profit > min_profit:
                            results.append(result)
        return results

    def find_opportunities(self, prices):
        # Для совместимости с ботом: получаем ликвидность (можно доработать)
        liquidity = {dex: {pair: 10000 for pair in prices[dex]} for dex in prices}  # mock
        return self.find_2way_arbitrage(prices, liquidity, min_profit=self.config.min_profit)
