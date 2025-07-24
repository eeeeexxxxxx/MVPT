import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
import time

LOG_FILE = "arbitrage_history.csv"
MODEL_FILE = "arbitrage_ml_model.pkl"

FEATURES = [
    "spread", "liq_buy", "liq_sell", "slippage", "fee_total",
    "delay", "oracle_deviation", "pair", "buy_dex", "sell_dex"
]

def train_model():
    df = pd.read_csv(LOG_FILE)
    # Преобразуем категориальные признаки
    df = pd.get_dummies(df, columns=["pair", "buy_dex", "sell_dex"])
    X = df[ [col for col in df.columns if col in FEATURES or col.startswith("pair_") or col.startswith("buy_dex_") or col.startswith("sell_dex_")] ]
    y = df["result"]
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump((model, X.columns.tolist()), MODEL_FILE)
    print("ML-модель обучена и сохранена.")

def auto_train_model(poll_interval=60):
    """
    Автоматически переобучает модель при появлении новых данных в истории.
    poll_interval: частота проверки (секунд)
    """
    last_size = 0
    if os.path.exists(LOG_FILE):
        last_size = os.path.getsize(LOG_FILE)
    while True:
        time.sleep(poll_interval)
        if not os.path.exists(LOG_FILE):
            continue
        size = os.path.getsize(LOG_FILE)
        if size != last_size:
            print("[AI TRAINER] Обнаружены новые данные, переобучаю модель...")
            train_model()
            last_size = size

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        auto_train_model()
    else:
        train_model() 