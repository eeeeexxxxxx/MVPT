import time
from config import Config
from dex_clients import DexClients
from arbitrage import ArbitrageFinder
from telegram_alerts import send_telegram_message
from flashloan_executor import FlashLoanExecutor
from ai_predictor import ArbitrageAIPredictor
from ai_logger import log_arbitrage


def main():
    config = Config()
    dex_clients = DexClients(config)
    arbitrage_finder = ArbitrageFinder(dex_clients, config)
    flashloan_executor = FlashLoanExecutor(config)
    ai = ArbitrageAIPredictor()
    sent_opps = set()  # Для фильтрации повторных сигналов
    print("[INFO] Arbitrage bot started.")
    while True:
        prices = dex_clients.fetch_all_prices()
        opportunities = arbitrage_finder.find_opportunities(prices)
        if opportunities:
            for opp in opportunities:
                opp_key = f"{opp['pair']}|{opp['buy_on']}|{opp['sell_on']}|{opp['buy_price']:.4f}|{opp['sell_price']:.4f}|{opp.get('amount', 0)}"
                if opp_key in sent_opps:
                    continue
                # AI-фильтрация
                features = {
                    "spread": opp["spread"],
                    "liq_buy": opp.get("liq_buy", 0),
                    "liq_sell": opp.get("liq_sell", 0),
                    "slippage": opp.get("slippage", 0),
                    "fee_total": opp.get("fee_total", 0),
                    "delay": opp.get("delay", 0),
                    "oracle_deviation": opp.get("oracle_deviation", 0),
                    "pair": opp["pair"],
                    "buy_dex": opp["buy_on"],
                    "sell_dex": opp["sell_on"]
                }
                prob = ai.predict(features)
                if prob < 0.9:
                    print(f"[AI] Сделка отклонена: вероятность плюса {prob:.2f}")
                    log_arbitrage(features, 0, opp.get("profit", 0))
                    continue
                sent_opps.add(opp_key)
                msg = (
                    f"*Arbitrage Opportunity!*
"
                    f"Pair: `{opp['pair']}`\n"
                    f"Buy on: `{opp['buy_on']}` at `{opp['buy_price']}`\n"
                    f"Sell on: `{opp['sell_on']}` at `{opp['sell_price']}`\n"
                    f"Profit: `${opp['profit']:.2f}`\n"
                    f"Spread: `{opp['spread']:.4f}`\n"
                )
                send_telegram_message(config.telegram_token, config.telegram_chat_id, msg)
                # Вызов арбитражной транзакции
                flashloan_executor.execute_flashloan_arbitrage(
                    amount=opp.get('amount', 0),
                    buy_dex=opp['buy_on'],
                    sell_dex=opp['sell_on'],
                    buy_price=opp['buy_price'],
                    sell_price=opp['sell_price'],
                    pair=opp['pair']
                )
                log_arbitrage(features, 1, opp.get("profit", 0))
            print(f"[ARBITRAGE] Opportunities found: {opportunities}")
        time.sleep(config.poll_interval)

if __name__ == "__main__":
    main()
