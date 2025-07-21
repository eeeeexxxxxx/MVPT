import requests
from solana.rpc.api import Client
from pythclient.pythaccounts import PythPriceAccount
from pythclient.solana import SolanaClient

PYTH_SOL_USDC_PRICE_ACCOUNT = "J83GJsk6b5bGzA2Fz3p8QwFqvQy1j6K9d9c6j6N8k1h"  # mainnet

class DexClients:
    def __init__(self, config):
        self.config = config

    def fetch_orca_price(self, pair="SOL/USDC"):
        # Orca API v2: https://api.orca.so/v1/markets
        try:
            resp = requests.get("https://api.orca.so/v1/markets")
            data = resp.json()
            if pair in data["markets"]:
                price = float(data["markets"][pair]["currentPrice"])
                return price
        except Exception as e:
            print(f"[ERROR] Orca price fetch failed: {e}")
        return None

    def fetch_raydium_price(self, pair="SOL/USDC"):
        # Raydium API: https://api.raydium.io/v2/sdk/liquidity/mainnet
        try:
            resp = requests.get("https://api.raydium.io/v2/sdk/liquidity/mainnet")
            data = resp.json()
            # Найти пул SOL/USDC
            for pool in data:
                if (pool.get("baseMint") == "So11111111111111111111111111111111111111112" and
                    pool.get("quoteMint") == "EPjFWdd5AufqSSqeM2q8VsJb9G9Z8k8b5uF9Qh6b6h8"):
                    # Цена = quote/base
                    price = float(pool["quoteReserve"])/float(pool["baseReserve"])
                    return price
        except Exception as e:
            print(f"[ERROR] Raydium price fetch failed: {e}")
        return None

    def fetch_jupiter_price(self, pair="SOL/USDC"):
        # Jupiter quote API: https://quote-api.jup.ag/v6/quote
        try:
            resp = requests.get(
                "https://quote-api.jup.ag/v6/quote",
                params={"inputMint": "So11111111111111111111111111111111111111112", "outputMint": "EPjFWdd5AufqSSqeM2q8VsJb9G9Z8k8b5uF9Qh6b6h8", "amount": 100000000, "slippageBps": 10}
            )
            data = resp.json()
            if "data" in data and data["data"]:
                price = float(data["data"][0]["outAmount"]) / 100000000
                return price
        except Exception as e:
            print(f"[ERROR] Jupiter price fetch failed: {e}")
        return None

    def fetch_pyth_price(self):
        # Получение справедливой цены SOL/USDC из Pyth
        try:
            solana_client = SolanaClient(endpoint=self.config.solana_rpc)
            price_account = PythPriceAccount(PYTH_SOL_USDC_PRICE_ACCOUNT, solana_client)
            price_data = price_account.fetch()
            price = price_data['price']
            return price
        except Exception as e:
            print(f"[ERROR] Pyth price fetch failed: {e}")
        return None

    def fetch_all_prices(self):
        # Получаем реальные цены с DEX
        prices = {}
        orca_price = self.fetch_orca_price()
        if orca_price:
            prices["orca"] = {"SOL/USDC": orca_price}
        raydium_price = self.fetch_raydium_price()
        if raydium_price:
            prices["raydium"] = {"SOL/USDC": raydium_price}
        jupiter_price = self.fetch_jupiter_price()
        if jupiter_price:
            prices["jupiter"] = {"SOL/USDC": jupiter_price}
        pyth_price = self.fetch_pyth_price() if self.config.pyth_oracle else None
        if pyth_price:
            prices["pyth"] = {"SOL/USDC": pyth_price}
        return prices
