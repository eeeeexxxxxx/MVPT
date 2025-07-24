import pandas as pd
import os

LOG_FILE = "arbitrage_history.csv"

def log_arbitrage(opportunity, result, profit):
    """
    opportunity: dict с параметрами сделки (DEX, спред, ликвидность и т.д.)
    result: 1 (плюс) или 0 (минус)
    profit: фактический профит в $
    """
    row = opportunity.copy()
    row['result'] = result
    row['profit'] = profit
    df = pd.DataFrame([row])
    if not os.path.exists(LOG_FILE):
        df.to_csv(LOG_FILE, index=False)
    else:
        df.to_csv(LOG_FILE, mode='a', header=False, index=False) 