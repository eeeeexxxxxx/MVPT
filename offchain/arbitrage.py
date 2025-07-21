class ArbitrageFinder:
    def __init__(self, dex_clients, config):
        self.dex_clients = dex_clients
        self.config = config

    def calc_profit(self, buy_price, sell_price, amount, buy_fee, sell_fee, flash_loan_fee):
        # amount — сумма в базовой валюте (например, SOL)
        buy_cost = buy_price * amount * (1 + buy_fee)
        sell_revenue = sell_price * amount * (1 - sell_fee)
        loan_fee = buy_price * amount * flash_loan_fee
        profit = sell_revenue - buy_cost - loan_fee
        return profit

    def find_opportunities(self, prices):
        result = []
        pairs = set()
        for dex, pairs_prices in prices.items():
            for pair in pairs_prices:
                pairs.add(pair)
        for pair in pairs:
            best_bid = None
            best_ask = None
            best_bid_dex = None
            best_ask_dex = None
            for dex, pairs_prices in prices.items():
                if dex == "pyth":
                    continue
                price = pairs_prices.get(pair)
                if price is not None:
                    if best_bid is None or price > best_bid:
                        best_bid = price
                        best_bid_dex = dex
                    if best_ask is None or price < best_ask:
                        best_ask = price
                        best_ask_dex = dex
            fair_price = prices.get("pyth", {}).get(pair)
            if fair_price:
                deviation_bid = abs(best_bid - fair_price) / fair_price
                deviation_ask = abs(best_ask - fair_price) / fair_price
                if deviation_bid > 0.03 or deviation_ask > 0.03:
                    continue
            if best_bid is not None and best_ask is not None and best_bid > best_ask * 1.001:
                # Расчёт потенциальной прибыли
                amount = 10  # пример: 10 SOL, можно сделать параметром
                buy_fee = self.config.dex_fees.get(best_ask_dex, 0.0025)
                sell_fee = self.config.dex_fees.get(best_bid_dex, 0.0025)
                flash_loan_fee = self.config.flash_loan_fee
                profit = self.calc_profit(buy_price=best_ask, sell_price=best_bid, amount=amount, buy_fee=buy_fee, sell_fee=sell_fee, flash_loan_fee=flash_loan_fee)
                if profit < self.config.min_profit:
                    continue
                result.append({
                    "pair": pair,
                    "buy_on": best_ask_dex,
                    "sell_on": best_bid_dex,
                    "buy_price": best_ask,
                    "sell_price": best_bid,
                    "spread": best_bid - best_ask,
                    "fair_price": fair_price,
                    "amount": amount,
                    "profit": profit
                })
        return result
