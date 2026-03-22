import aiosqlite
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    deadline DATETIME NOT NULL,
                    is_done INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    notified_1day INTEGER DEFAULT 0,
                    notified_3hours INTEGER DEFAULT 0,
                    notified_30min INTEGER DEFAULT 0
                )
            """)
            await db.commit()

    async def add_task(self, user_id: int, subject: str, title: str,
                       description: Optional[str], deadline: datetime) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "INSERT INTO tasks (user_id, subject, title, description, deadline) VALUES (?, ?, ?, ?, ?)",
                (user_id, subject, title, description, deadline.strftime("%Y-%m-%d %H:%M:%S"))
            )
            await db.commit()
            return cursor.lastrowid

    async def get_active_tasks(self, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND is_done = 0 ORDER BY deadline ASC",
                (user_id,)
            )
            return await cursor.fetchall()

    async def get_done_tasks(self, user_id: int) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND is_done = 1 ORDER BY deadline DESC LIMIT 20",
                (user_id,)
            )
            return await cursor.fetchall()

    async def get_tasks_by_subject(self, user_id: int, subject: str) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE user_id = ? AND subject LIKE ? AND is_done = 0 ORDER BY deadline ASC",
                (user_id, f"%{subject}%")
            )
            return await cursor.fetchall()

    async def get_upcoming_tasks(self, user_id: int, hours: int = 48) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """SELECT * FROM tasks WHERE user_id = ? AND is_done = 0
                   AND deadline BETWEEN datetime('now') AND datetime('now', ? || ' hours')
                   ORDER BY deadline ASC""",
                (user_id, str(hours))
            )
            return await cursor.fetchall()

    async def get_task_by_id(self, task_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id)
            )
            return await cursor.fetchone()

    async def mark_done(self, task_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE tasks SET is_done = 1 WHERE id = ? AND user_id = ?",
                (task_id, user_id)
            )
            await db.commit()

    async def delete_task(self, task_id: int, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id)
            )
            await db.commit()

    async def update_task(self, task_id: int, user_id: int, subject: str,
                          title: str, description: Optional[str], deadline: datetime):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """UPDATE tasks SET subject=?, title=?, description=?, deadline=?,
                   notified_1day=0, notified_3hours=0, notified_30min=0
                   WHERE id = ? AND user_id = ?""",
                (subject, title, description, deadline.strftime("%Y-%m-%d %H:%M:%S"), task_id, user_id)
            )
            await db.commit()

    async def get_all_active_tasks(self) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM tasks WHERE is_done = 0 AND deadline > datetime('now')"
            )
            return await cursor.fetchall()

    async def set_notified(self, task_id: int, field: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE tasks SET {field} = 1 WHERE id = ?", (task_id,))
            await db.commit()

    async def get_subjects(self, user_id: int) -> list[str]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT DISTINCT subject FROM tasks WHERE user_id = ? AND is_done = 0 ORDER BY subject",
                (user_id,)
            )
            rows = await cursor.fetchall()
            return [r[0] for r in rows]