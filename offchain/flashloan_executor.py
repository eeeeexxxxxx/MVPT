from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.publickey import PublicKey
from anchorpy import Program, Provider, Wallet
import asyncio
import base58
import json

ARBITRAGE_IDL_PATH = "../arbitrage_program/target/idl/arbitrage_program.json"
ARBITRAGE_PROGRAM_ID = "33BQPv9UU9moaQPah9umUad4ovijbF2TVmxcGdSmeSJR"  # заменить на актуальный

async def execute_arbitrage_anchorpy(config, params, accounts):
    # Загрузка IDL
    with open(ARBITRAGE_IDL_PATH, "r") as f:
        idl = json.load(f)
    program_id = PublicKey(ARBITRAGE_PROGRAM_ID)
    client = AsyncClient(config.solana_rpc)
    wallet = Wallet(Keypair.from_secret_key(base58.b58decode(config.wallet_private_key)))
    provider = Provider(client, wallet)
    program = Program(idl, program_id, provider)
    # Вызов инструкции
    tx = await program.rpc["execute_arbitrage"](
        params,
        ctx={
            "accounts": accounts,
            "signers": [wallet.payer],
        }
    )
    print(f"[ANCHORPY] TX sent: {tx}")
    await client.close()

# Пример использования:
# params = {
#     "amount": 1000000,
#     "min_profit": 1000,
#     "buy_pool": "...",
#     "sell_pool": "...",
#     "token_mint": "..."
# }
# accounts = {
#     "user": "...",
#     "marginfi_group": "...",
#     "marginfi_account": "...",
#     "marginfi_bank": "...",
#     "buy_pool": "...",
#     "sell_pool": "...",
#     "user_token_account": "...",
#     "temp_token_account": "...",
#     "marginfi_program": "...",
#     "token_program": "...",
#     "system_program": "...",
#     "rent": "...",
#     "associated_token_program": "..."
# }
# asyncio.run(execute_arbitrage_anchorpy(config, params, accounts)) 