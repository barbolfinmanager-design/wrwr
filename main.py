import asyncio
import uvicorn
from aiogram import Bot

from config import config
from bot import dp
import db

async def run_bot():
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN не настроен")
    bot = Bot(config.bot_token)
    await dp.start_polling(bot)

async def run_web():
    server = uvicorn.Server(
        uvicorn.Config("app:app", host=config.host, port=config.port, log_level="info")
    )
    await server.serve()

async def main():
    await db.init_db()
    await asyncio.gather(run_web(), run_bot())

if __name__ == "__main__":
    asyncio.run(main())
