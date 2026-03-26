import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database import Database
from handlers import TaskHandlers
from scheduler import TaskScheduler

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class DeadlineBot:
    def __init__(self):
        self.token = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
        self.db_path = os.getenv("DB_PATH", "deadlines.db")

        self.bot = Bot(token=self.token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.db = Database(self.db_path)
        self.scheduler = TaskScheduler(self.bot, self.db)
        self.handlers = TaskHandlers(self.db)

        self.dp.include_router(self.handlers.router)

    async def start(self):
        await self.db.init()
        self.scheduler.start()
        logging.info("✅ DeadlineBot запущен!")
        try:
            await self.dp.start_polling(
                self.bot,
                allowed_updates=self.dp.resolve_used_update_types()
            )
        finally:
            self.scheduler.stop()
            await self.bot.session.close()
            logging.info("Bot остановлен.")


if __name__ == "__main__":
    asyncio.run(DeadlineBot().start())