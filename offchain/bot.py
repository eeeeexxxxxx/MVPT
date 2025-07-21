import time
from config import Config
from dex_clients import DexClients
from arbitrage import ArbitrageFinder
from telegram_alerts import send_telegram_message
from flashloan_executor import FlashLoanExecutor


def main():
    config = Config()
    dex_clients = DexClients(config)
    arbitrage_finder = ArbitrageFinder(dex_clients, config)
    flashloan_executor = FlashLoanExecutor(config)
    sent_opps = set()  # Для фильтрации повторных сигналов
    print("[INFO] Arbitrage bot started.")
    while True:
        prices = dex_clients.fetch_all_prices()
        opportunities = arbitrage_finder.find_opportunities(prices)
        if opportunities:
            for opp in opportunities:
                opp_key = f"{opp['pair']}|{opp['buy_on']}|{opp['sell_on']}|{opp['buy_price']:.4f}|{opp['sell_price']:.4f}|{opp['amount']}"
                if opp_key in sent_opps:
                    continue
                sent_opps.add(opp_key)
                msg = (
                    f"*Arbitrage Opportunity!*
"
                    f"Pair: `{opp['pair']}`\n"
                    f"Buy on: `{opp['buy_on']}` at `{opp['buy_price']}`\n"
                    f"Sell on: `{opp['sell_on']}` at `{opp['sell_price']}`\n"
                    f"Amount: `{opp['amount']}`\n"
                    f"Profit: `${opp['profit']:.2f}`\n"
                    f"Spread: `{opp['spread']:.4f}`\n"
                    f"Fair price: `{opp['fair_price']}`"
                )
                send_telegram_message(config.telegram_token, config.telegram_chat_id, msg)
                # Вызов арбитражной транзакции (заглушка)
                flashloan_executor.execute_flashloan_arbitrage(
                    amount=opp['amount'],
                    buy_dex=opp['buy_on'],
                    sell_dex=opp['sell_on'],
                    buy_price=opp['buy_price'],
                    sell_price=opp['sell_price'],
                    pair=opp['pair']
                )
            print(f"[ARBITRAGE] Opportunities found: {opportunities}")
        time.sleep(config.poll_interval)

if __name__ == "__main__":
    main()
