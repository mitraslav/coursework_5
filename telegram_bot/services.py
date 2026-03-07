import requests
from django.conf import settings


def send_telegram_message(chat_id: str, text: str) -> None:
    url = f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text,
    }
    requests.post(url, json=payload, timeout=10)