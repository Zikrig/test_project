import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _require_int(name: str, *aliases: str) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        for alias in aliases:
            raw = os.getenv(alias, "").strip()
            if raw:
                break
    if not raw:
        raise ValueError(
            f"Set {name} in .env to a numeric Telegram user id "
            f"(aliases tried: {', '.join(aliases) or 'none'})."
        )
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.environ["BOT_TOKEN"]
    admin_telegram_id: int = _require_int(
        "ADMIN_TELEGRAM_ID", "TELEGRAM_USER_ID"
    )
    table_id: str = os.environ["TABLE_ID"]
    credentials_path: str = os.getenv("CREDENTIALS_PATH", "credentials.json")
    database_path: str = os.getenv("DATABASE_PATH", "data/db/bot.db")
    welcome_image_path: str = os.getenv(
        "WELCOME_IMAGE_PATH", "data/images/image.png"
    )
    # Example: socks5://127.0.0.1:1080 or http://127.0.0.1:8080
    proxy_url: str | None = os.getenv("PROXY_URL", "").strip() or None


settings = Settings()
