import asyncio
import uvicorn
from aiogram import Bot
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from config import config
from bot import dp
import db

bot_instance = None

async def run_bot():
    global bot_instance
    if not config.bot_token:
        print("⚠️  BOT_TOKEN не установлен. Бот не будет запущен.")
        return
    print("🤖 Запуск Telegram бота...")
    bot_instance = Bot(config.bot_token)
    try:
        await dp.start_polling(bot_instance)
    except Exception as e:
        print(f"❌ Ошибка бота: {e}")
    finally:
        if bot_instance:
            await bot_instance.session.close()

async def run_web():
    print(f"🌐 Запуск веб-сервера на http://{config.host}:{config.port}")
    config_obj = uvicorn.Config(
        "app:app",
        host=config.host,
        port=config.port,
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config_obj)
    try:
        await server.serve()
    except Exception as e:
        print(f"❌ Ошибка сервера: {e}")

async def main():
    print("\n" + "="*50)
    print("🚀 Sharp Tongue Mini App запускается...")
    print("="*50 + "\n")
    
    # Инициализация БД
    try:
        await db.init_db()
        print("✅ База данных инициализирована")
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        sys.exit(1)
    
    # Запускаем веб-сервер (обязательно)
    if config.bot_token:
        print("📋 Запуск: Веб-сервер + Telegram бот")
        try:
            await asyncio.gather(
                run_web(),
                run_bot(),
                return_exceptions=True
            )
        except KeyboardInterrupt:
            print("\n⏹️  Приложение остановлено")
    else:
        print("📋 Запуск: Только веб-сервер (без бота)")
        print("💡 Совет: Добавьте BOT_TOKEN в .env файл для запуска бота")
        try:
            await run_web()
        except KeyboardInterrupt:
            print("\n⏹️  Приложение остановлено")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Выход")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
