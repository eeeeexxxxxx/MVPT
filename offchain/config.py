class Config:
    def __init__(self):
        self.dex_list = ["orca", "raydium", "jupiter"]
        self.poll_interval = 2  # секунд между опросами
        self.solana_rpc = "https://api.mainnet-beta.solana.com"  # заменить на свой RPC
        self.pyth_oracle = True  # использовать ли оракул для фильтрации
        self.dex_fees = {  # комиссии DEX в долях
            "orca": 0.0025,
            "raydium": 0.0025,
            "jupiter": 0.0030
        }
        self.flash_loan_fee = 0.0008  # комиссия MarginFi (пример)
        self.min_profit = 1.0  # минимальный профит в USDC для сделки
        # Telegram
        self.telegram_token = "<YOUR_TELEGRAM_BOT_TOKEN>"
        self.telegram_chat_id = "<YOUR_CHAT_ID>"
        # Solana wallet
        self.wallet_private_key = "<YOUR_PRIVATE_KEY>"  # base58 или список чисел
