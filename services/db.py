import aiosqlite
from pathlib import Path

from config import settings


async def init_db() -> None:
    path = Path(settings.database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(path) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                username TEXT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        await db.commit()


async def save_registration(
    telegram_id: int,
    username: str | None,
    name: str,
    age: int,
    source: str,
) -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            INSERT INTO registrations (telegram_id, username, name, age, source)
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_id, username, name, age, source),
        )
        await db.commit()
