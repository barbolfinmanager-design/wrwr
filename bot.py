import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)
from aiogram.enums import ParseMode

from config import config
import db

dp = Dispatcher()

def app_button():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐸 Открыть Sharp Tongue", web_app=WebAppInfo(url=config.webapp_url))]
    ])

@dp.message(CommandStart())
async def start(message: Message):
    await db.ensure_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        config.start_ton_nano
    )
    text = (
        "💋 <b>Sharp Tongue</b>\n\n"
        "Покупай неулучшенный Sharp Tongue за ⭐, открывай бесплатный Upgrade "
        "и торгуй ими на внутреннем маркете."
    )
    if config.webapp_url:
        await message.answer(text, reply_markup=app_button(), parse_mode=ParseMode.HTML)
    else:
        await message.answer(text + "\n\nWEBAPP_URL ещё не настроен.", parse_mode=ParseMode.HTML)

@dp.message(Command("paysupport"))
async def paysupport(message: Message):
    await message.answer(
        "Поддержка платежей: обратитесь к администратору проекта. "
        "Сохраните дату покупки и Telegram payment charge id."
    )

@dp.pre_checkout_query()
async def pre_checkout(q: PreCheckoutQuery):
    minted = (await db.stats(q.from_user.id))["minted"]
    ok = (
        q.currency == "XTR"
        and q.invoice_payload == "sharp_tongue_v2"
        and q.total_amount == config.pepe_price_stars
        
    )
    await q.answer(ok=ok, error_message=None if ok else "Покупка недоступна.")

@dp.message(F.successful_payment)
async def paid(message: Message):
    p = message.successful_payment
    if p.currency != "XTR" or p.invoice_payload != "sharp_tongue_v2":
        return
    await db.ensure_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        config.start_ton_nano
    )
    item = await db.mint_with_stars(message.from_user.id, p.telegram_payment_charge_id, p.total_amount)
    if not item:
        await message.answer("Платёж получен, но mint не завершён. Используйте /paysupport.")
        return
    await message.answer(
        f"✅ Sharp Tongue purchase #{item['serial']} добавлен в инвентарь.\n"
        "Открой Mini App и сделай бесплатный Upgrade.",
        reply_markup=app_button() if config.webapp_url else None
    )

async def main():
    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN не настроен")
    await db.init_db()
    bot = Bot(config.bot_token)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
