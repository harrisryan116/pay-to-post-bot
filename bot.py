import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram.filters import Command
import aiohttp
import database

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
NOWPAY_API_KEY = os.getenv("NOWPAYMENTS_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

PRICE_USD = 1  # $1 per message

async def create_invoice(user_id: int):
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {
        "x-api-key": NOWPAY_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "price_amount": PRICE_USD,
        "price_currency": "usd",
        "pay_currency": "usdttrc20",
        "order_id": str(user_id),
        "success_url": "https://t.me/pay_to_post_bot",
        "cancel_url": "https://t.me/pay_to_post_bot"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            return await resp.json()

@dp.message(F.chat.type == ChatType.SUPERGROUP)
async def block_unpaid(message: Message):

    user_id = message.from_user.id

    if database.has_credit(user_id):
        database.use_credit(user_id)
        return
    else:
        try:
            await message.delete()
        except:
            pass

        invoice = await create_invoice(user_id)

        if "invoice_url" in invoice:
            link = invoice["invoice_url"]
            text = (
                "⚠️ Posting in this group costs **$1**.\n\n"
                "💳 Pay below to unlock **ONE message**:\n\n"
                f"[Click here to pay]({link})"
            )
        else:
            text = "❌ Failed to generate payment invoice. Try again."

        try:
            await bot.send_message(user_id, text)
        except:
            pass

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Bot is running!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
