import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, BotCommand
)
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from config import config
import db

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()

def app_button():
    """Кнопка для открытия веб-приложения"""
    if not config.webapp_url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=WebAppInfo(url=config.webapp_url))]
    ])

def main_menu():
    """Главное меню с кнопками"""
    if not config.webapp_url:
        return None
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=WebAppInfo(url=config.webapp_url))]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    """Обработчик команды /start"""
    logger.info(f"🔔 Получена команда /start от пользователя {message.from_user.id} (@{message.from_user.username})")
    
    try:
        await db.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            config.start_ton_nano
        )
        logger.info(f"✅ Пользователь {message.from_user.id} создан/обновлен в БД")
    except Exception as e:
        logger.error(f"❌ Ошибка при создании пользователя: {e}")
    
    text = (
        "💋 <b>Sharp Tongue</b>\n\n"
        "Покупай неулучшенный Sharp Tongue за ⭐, открывай бесплатный Upgrade "
        "и торгуй ими на внутреннем маркете."
    )
    
    try:
        if config.webapp_url:
            logger.info(f"✅ WEBAPP_URL установлен: {config.webapp_url}")
            await message.answer(text, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
        else:
            logger.warning("⚠️ WEBAPP_URL не установлен")
            await message.answer(
                text + "\n\n⚠️ <b>WEBAPP_URL</b> еще не настроен в переменных окружения.",
                parse_mode=ParseMode.HTML
            )
    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API в start: {e}")

@dp.message(Command("app"))
async def open_app(message: Message):
    """Команда для открытия приложения"""
    logger.info(f"🔔 Получена команда /app от пользователя {message.from_user.id}")
    
    try:
        if config.webapp_url:
            text = "🚀 <b>Sharp Tongue Mini App</b>\n\nНажми кнопку ниже, чтобы открыть приложение."
            await message.answer(text, reply_markup=app_button(), parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                "⚠️ Приложение еще не доступно. Установите WEBAPP_URL.",
                parse_mode=ParseMode.HTML
            )
    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API в open_app: {e}")

@dp.message(Command("paysupport"))
async def paysupport(message: Message):
    """Команда поддержки платежей"""
    logger.info(f"🔔 Получена команда /paysupport от пользователя {message.from_user.id}")
    
    try:
        await message.answer(
            "💬 <b>Поддержка платежей</b>\n\n"
            "Если у вас есть проблемы с платежом:\n\n"
            "1. Сохраните дату покупки\n"
            "2. Сохраните Telegram payment charge id\n"
            "3. Свяжитесь с администратором проекта",
            parse_mode=ParseMode.HTML
        )
    except TelegramAPIError as e:
        logger.error(f"❌ Ошибка Telegram API в paysupport: {e}")

@dp.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    """Проверка платежа"""
    logger.info(f"💳 Проверка платежа от пользователя {q.from_user.id}")
    
    try:
        stats = await db.stats(q.from_user.id)
        ok = (
            q.currency == "XTR"
            and q.invoice_payload == "sharp_tongue_v2"
            and q.total_amount == config.pepe_price_stars
        )
        
        if ok:
            logger.info(f"✅ Платеж одобрен для пользователя {q.from_user.id}")
        else:
            logger.warning(f"❌ Платеж отклонен для пользователя {q.from_user.id}")
        
        await q.answer(ok=ok, error_message=None if ok else "Покупка недоступна.")
    except Exception as e:
        logger.error(f"❌ Ошибка в pre_checkout: {e}")
        await q.answer(ok=False, error_message="Ошибка при проверке платежа")

@dp.message(F.successful_payment)
async def paid(message: Message):
    """Обработка успешного платежа"""
    logger.info(f"✅ Успешный платеж от пользователя {message.from_user.id}")
    
    try:
        p = message.successful_payment
        
        # Проверка типа платежа
        if p.currency != "XTR" or p.invoice_payload != "sharp_tongue_v2":
            logger.warning(f"⚠️ Платеж неправильного типа от {message.from_user.id}")
            return
        
        # Создание пользователя если не существует
        await db.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            config.start_ton_nano
        )
        
        # Mint покупки
        item = await db.mint_with_stars(
            message.from_user.id,
            p.telegram_payment_charge_id,
            p.total_amount
        )
        
        if not item:
            logger.error(f"❌ Ошибка mint для пользователя {message.from_user.id}")
            await message.answer(
                "❌ Платеж получен, но mint не завершен.\n"
                "Используйте /paysupport для поддержки."
            )
            return
        
        logger.info(f"✅ Mint успешен для пользователя {message.from_user.id}, serial: {item['serial']}")
        
        await message.answer(
            f"✅ <b>Sharp Tongue #{item['serial']} добавлен</b>\n\n"
            "Открой Mini App и сделай бесплатный Upgrade.",
            reply_markup=app_button() if config.webapp_url else None,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в paid: {e}")
        await message.answer(
            "❌ Ошибка при обработке платежа.\n"
            "Используйте /paysupport для контакта."
        )

async def set_bot_commands(bot: Bot):
    """Установка команд для бота"""
    logger.info("⚙️ Установка команд бота...")
    try:
        commands = [
            BotCommand(command="start", description="🚀 Начать"),
            BotCommand(command="app", description="🌐 Открыть приложение"),
            BotCommand(command="paysupport", description="💬 Поддержка платежей"),
        ]
        await bot.set_my_commands(commands)
        logger.info("✅ Команды установлены")
    except Exception as e:
        logger.error(f"❌ Ошибка при установке команд: {e}")

async def main():
    """Главная функция бота"""
    if not config.bot_token:
        logger.error("❌ BOT_TOKEN не установлен")
        return
    
    logger.info("="*50)
    logger.info("🤖 Запуск Telegram бота...")
    logger.info(f"Bot Token: {config.bot_token[:20]}...")
    logger.info(f"WebApp URL: {config.webapp_url or 'НЕ УСТАНОВЛЕН'}")
    logger.info("="*50)
    
    bot = Bot(token=config.bot_token)
    
    try:
        # Установка команд
        await set_bot_commands(bot)
        
        # Удаление старого webhook если был
        logger.info("🔄 Удаление старых webhook'ов...")
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook'и удалены")
        
        # Запуск polling
        logger.info("👂 Начинаю слушать обновления (polling)...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"❌ Ошибка в main: {e}")
    finally:
        await bot.session.close()
        logger.info("❌ Бот остановлен")

if __name__ == "__main__":
    asyncio.run(main())
