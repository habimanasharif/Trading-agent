"""Optional Telegram text/photo delivery. Configure tokens through environment variables."""
from __future__ import annotations
import os
from pathlib import Path
import requests


class TelegramNotifier:
    def __init__(self, token: str | None = None, chat_id: str | None = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        if not self.token or not self.chat_id:
            raise ValueError("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file")

    def send_message(self, text: str) -> None:
        response = requests.post(
            f"https://api.telegram.org/bot{self.token}/sendMessage",
            data={"chat_id": self.chat_id, "text": text}, timeout=20)
        response.raise_for_status()
        if not response.json().get("ok"):
            raise RuntimeError("Telegram did not accept the message")

    def send_photo(self, image_path: str | Path, caption: str) -> None:
        with Path(image_path).open("rb") as image_file:
            response = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendPhoto",
                data={"chat_id": self.chat_id, "caption": caption[:1024]},
                files={"photo": image_file}, timeout=45)
        response.raise_for_status()
        if not response.json().get("ok"):
            raise RuntimeError("Telegram did not accept the photo")
