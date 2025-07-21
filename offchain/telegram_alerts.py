import requests

def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        resp = requests.post(url, data=payload)
        if resp.status_code != 200:
            print(f"[ERROR] Telegram send failed: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Telegram send exception: {e}") 