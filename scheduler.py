from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from aiogram import Bot

from database import Database
from formatter import Formatter


class TaskScheduler:
    def __init__(self, bot: Bot, db: Database):
        self.bot = bot
        self.db = db
        self._scheduler = AsyncIOScheduler(timezone="UTC")
        self._scheduler.add_job(self._check_reminders, "interval", minutes=5)

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()

    async def _check_reminders(self):
        tasks = await self.db.get_all_active_tasks()
        now = datetime.utcnow()

        for task in tasks:
            await self._process_task(dict(task), now)

    async def _process_task(self, task: dict, now: datetime):
        deadline = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M:%S")
        diff = deadline - now

        if not task["notified_1day"] and timedelta(hours=23) <= diff <= timedelta(hours=25):
            await self._send_reminder(task, "⏰ 1 day until", "notified_1day")

        elif not task["notified_3hours"] and timedelta(hours=2, minutes=45) <= diff <= timedelta(hours=3, minutes=15):
            await self._send_reminder(task, "🔔 3 hours until", "notified_3hours")

        elif not task["notified_30min"] and timedelta(minutes=25) <= diff <= timedelta(minutes=35):
            await self._send_reminder(task, "🚨 30 minutes until", "notified_30min")

    async def _send_reminder(self, task: dict, label: str, field: str):
        await self.bot.send_message(
            task["user_id"],
            Formatter.task_reminder(task, label),
            parse_mode="HTML"
        )
        await self.db.set_notified(task["id"], field)