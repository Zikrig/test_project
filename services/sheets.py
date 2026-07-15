from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _client() -> gspread.Client:
    creds = Credentials.from_service_account_file(
        settings.credentials_path,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def append_registration(
    telegram_id: int,
    username: str | None,
    name: str,
    age: int,
    phone: str,
    source: str,
) -> None:
    client = _client()
    sheet = client.open_by_key(settings.table_id).sheet1
    sheet.append_row(
        [
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            str(telegram_id),
            username or "",
            name,
            age,
            phone,
            source,
        ],
        value_input_option="USER_ENTERED",
    )
