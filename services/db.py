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
                phone TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        await _ensure_column(db, "registrations", "phone", "TEXT NOT NULL DEFAULT ''")
        await db.commit()


async def _ensure_column(
    db: aiosqlite.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    async with db.execute(f"PRAGMA table_info({table})") as cursor:
        rows = await cursor.fetchall()
    names = {row[1] for row in rows}
    if column not in names:
        await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


async def save_registration(
    telegram_id: int,
    username: str | None,
    name: str,
    age: int,
    phone: str,
    source: str,
) -> None:
    async with aiosqlite.connect(settings.database_path) as db:
        await db.execute(
            """
            INSERT INTO registrations
                (telegram_id, username, name, age, phone, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (telegram_id, username, name, age, phone, source),
        )
        await db.commit()
