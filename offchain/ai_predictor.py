import joblib
import pandas as pd
import numpy as np
import os
import time

MODEL_FILE = "arbitrage_ml_model.pkl"

class ArbitrageAIPredictor:
    def __init__(self):
        self.model, self.columns = joblib.load(MODEL_FILE)
        self.last_mtime = os.path.getmtime(MODEL_FILE)

    def reload_if_needed(self):
        mtime = os.path.getmtime(MODEL_FILE)
        if mtime != self.last_mtime:
            print("[AI] Обнаружено обновление ML-модели, перезагружаю...")
            self.model, self.columns = joblib.load(MODEL_FILE)
            self.last_mtime = mtime

    def predict(self, opportunity: dict) -> float:
        self.reload_if_needed()
        df = pd.DataFrame([opportunity])
        for col in self.columns:
            if col not in df.columns:
                df[col] = 0
        df = df[self.columns]
        proba = self.model.predict_proba(df)[0, 1]
        return proba

# Пример использования:
# ai = ArbitrageAIPredictor()
# prob = ai.predict({
#     "spread": 0.003,
#     "liq_buy": 10000,
#     "liq_sell": 12000,
#     "slippage": 0.0005,
#     "fee_total": 0.0015,
#     "delay": 0.2,
#     "oracle_deviation": 0.001,
#     "pair": "SOL/USDC",
#     "buy_dex": "orca",
#     "sell_dex": "raydium"
# })
# if prob > 0.9:
#     ... # Совершаем сделку 