import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from config import config
import db

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
        [InlineKeyboardButton(text="🚀 Открыть приложение", web_app=WebAppInfo(url=config.webapp_url))],
        [InlineKeyboardButton(text="📞 Поддержка", callback_data="support")]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    try:
        await db.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            config.start_ton_nano
        )
    except Exception as e:
        print(f"⚠️  Ошибка DB в start: {e}")
    
    text = (
        "💋 <b>Sharp Tongue</b>\n\n"
        "Покупай неулучшенный Sharp Tongue за ⭐, открывай бесплатный Upgrade "
        "и торгуй ими на внутреннем маркете."
    )
    
    try:
        if config.webapp_url:
            await message.answer(text, reply_markup=main_menu(), parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                text + "\n\n⚠️ <b>WEBAPP_URL</b> ещё не настроен в переменных окружения.",
                parse_mode=ParseMode.HTML
            )
    except TelegramAPIError as e:
        print(f"❌ Ошибка Telegram API: {e}")

@dp.message(Command("app"))
async def open_app(message: Message):
    """Команда для открытия приложения"""
    try:
        if config.webapp_url:
            text = "🚀 <b>Sharp Tongue Mini App</b>\n\nНажми кнопку ниже, чтобы открыть приложение."
            await message.answer(text, reply_markup=app_button(), parse_mode=ParseMode.HTML)
        else:
            await message.answer(
                "⚠️ Приложение ещё не доступно. Установите WEBAPP_URL.",
                parse_mode=ParseMode.HTML
            )
    except TelegramAPIError as e:
        print(f"❌ Ошибка Telegram API: {e}")

@dp.message(Command("paysupport"))
async def paysupport(message: Message):
    try:
        await message.answer(
            "Поддержка платежей: обратитесь к администратору проекта. "
            "Сохраните дату покупки и Telegram payment charge id."
        )
    except TelegramAPIError as e:
        print(f"❌ Ошибка Telegram API: {e}")

@dp.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    try:
        stats = await db.stats(q.from_user.id)
        ok = (
            q.currency == "XTR"
            and q.invoice_payload == "sharp_tongue_v2"
            and q.total_amount == config.pepe_price_stars
        )
        await q.answer(ok=ok, error_message=None if ok else "Покупка недоступна.")
    except Exception as e:
        print(f"⚠️  Ошибка в pre_checkout: {e}")
        await q.answer(ok=False, error_message="Ошибка при проверке платежа")

@dp.message(F.successful_payment)
async def paid(message: Message):
    try:
        p = message.successful_payment
        if p.currency != "XTR" or p.invoice_payload != "sharp_tongue_v2":
            return
        
        await db.ensure_user(
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            config.start_ton_nano
        )
        
        item = await db.mint_with_stars(
            message.from_user.id,
            p.telegram_payment_charge_id,
            p.total_amount
        )
        
        if not item:
            await message.answer("Платёж получен, но mint не завершён. Используйте /paysupport.")
            return
        
        await message.answer(
            f"✅ Sharp Tongue purchase #{item['serial']} добавлен в инвентарь.\n"
            "Открой Mini App и сделай бесплатный Upgrade.",
            reply_markup=app_button() if config.webapp_url else None
        )
    except Exception as e:
        print(f"⚠️  Ошибка в paid: {e}")
        await message.answer("❌ Ошибка при обработке платежа. Используйте /paysupport.")
