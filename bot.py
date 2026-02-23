import logging
import os
from aiogram import Bot, Dispatcher
from config.config import *
from database.database import *
from datetime import datetime
import games.games
from cryptopay.cryptopay import *
import asyncio
from admin.main import router as main_router
from aiogram import Bot, Dispatcher
from games.games import *
from aiogram.fsm.state import State, StatesGroup


class WalletStates(StatesGroup):
    waiting_for_wallet_address = State()  # состояние для ожидания кошелька

os.makedirs('logs', exist_ok=True)
log_file = f"logs/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

async def main():
    init_db()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(main_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Запуск бота...")
    asyncio.run(main())
