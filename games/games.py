import asyncio
import logging
import random
import sqlite3
import uuid
import random
from typing import Optional, List, Union
import re
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import F
import config.config
from igru.igru import *
from aiogram.filters import state
from games.keyboard import *
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Router
from config.config import *
from cryptopay.cryptopay import CryptoPayAPI, check_invoice_paid
from database.database import *
from keyboard.keyboard import *
from admin.keyboard import *
from admin.main import *
from aiocryptopay import AioCryptoPay
from igru.igru_logi import *
from aiogram.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from config.config import HEARTS_MULTIPLIER
from aiogram.fsm.state import StatesGroup, State

class HeartsGameState(StatesGroup):
    waiting_for_bet = State()

class BowlingGameState(StatesGroup):
    waiting_for_bet = State()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
cryptopay_api = CryptoPayAPI(CRYPTO_PAY_TOKEN)

router = Router()
user_languages = {}
invoices = {}

class WithdrawStates(StatesGroup):
    waiting_for_amount = State()
class DepositStates(StatesGroup):
    waiting_for_amount = State()
class DiceGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class SlotsGameState(StatesGroup):
    waiting_for_bet = State()
class DartsGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class FootballGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class BowlingGameState(StatesGroup):
    waiting_for_bet = State()
class BasketballGameState(StatesGroup):
    waiting_for_bet = State()
class EvenOddGameState(StatesGroup):
    waiting_for_bet = State()
class GuessNumberGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_number = State()
class DoubleDiceGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class MinesGameState(StatesGroup):
    waiting_for_bet = State()
class TowerGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_tower_choice = State()
    waiting_for_cell_choice = State()
class RPSGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class RussianRouletteGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_bullet_count = State()
class RouletteGameState(StatesGroup):
    waiting_for_bet = State()
    waiting_for_choice = State()
class Game21State(StatesGroup):
    waiting_for_bet = State()
    playing = State()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.username or message.from_user.first_name

    if not is_user_registered(user_id):
        add_user_if_not_exists(user_id, user_name)
        await message.answer(
            f"💎 Добро пожаловать в {NAME_CASINO} – мир азарта и больших выигрышей! 🎰 Наслаждайтесь лучшими коэффициентами 2x!\n\n"
            f"💰 Наш призовой фонд превышает $300! Погрузитесь в захватывающие игры: ищите сокровища в Минах 💣, покоряйте Башню 🛕, испытайте удачу в Рулетке 🎡 и откройте для себя множество других развлечений! 🎲🎯🎳🎮🎰\n\n"
            f"🚀 Наш канал с LIVE ставками\n\n"
            f"🌐 Выберите предпочитаемый язык и отправляйтесь в путешествие к победе! 🌟\n",
            parse_mode="HTML",
            reply_markup=language_inline_keyboard()
        )
    else:
        user_data = get_user_data(user_id)
        lang = user_languages.get(user_id, "russian")
        await send_language_welcome(message, message.from_user, lang)

@router.callback_query(F.data.startswith("language_"))
async def process_language_selection(callback: CallbackQuery):
    lang = callback.data.replace("language_", "")
    await send_language_welcome(callback.message, callback.from_user, lang)
    await callback.answer()

@router.message(F.text.in_({"/eng", "/ru"}))
async def switch_language_command(message: Message):
    lang = "english" if message.text == "/eng" else "russian"
    await send_language_welcome(message, message.from_user, lang)


async def send_language_welcome(target, user, lang: str):
    user_id = user.id
    user_name = user.username or user.first_name
    user_languages[user_id] = lang
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    if lang == "russian":
        text = (
            f"🎉 Добро пожаловать в {NAME_CASINO}!🎲🔥\n\n"
            f"💎 Ваш профиль ›\n"
            f"├ Текущий баланс: {user_data['balance']}$\n"
            f"├ Общий оборот: {user_data['total_turnover']}$\n"
            f"├ Пополнений: {user_data['deposits']}\n"
            f"└ Выводов: {user_data['withdrawals']}\n\n"
            f"💠 Наш <a href='https://t.me/+QDs9lK828w43ZTU6'>канал с Live ставками</a> 💥\n"
            f"🌐 /eng"
        )
    else:
        text = (
            f"🎉 Welcome to {NAME_CASINO}!🎲🔥\n\n"
            f"🎉 Добро пожаловать в {NAME_CASINO}!🎲🔥\n\n"
            f"💎 Your profile ›\n"
            f"├ Balance: {user_data['balance']}$\n"
            f"├ Total Turnover: {user_data['total_turnover']}$\n"
            f"├ Deposits: {user_data['deposits']}\n"
            f"└ Withdrawals: {user_data['withdrawals']}\n\n"
            f"💠 Our <a href='https://t.me/+QDs9lK828w43ZTU6'>Live betting channel</a> 💥\n"
            f"🌐 /ru"
        )
    reply_markup = start_bet_keyboard(user_id=user_id, lang=lang)

    await target.answer(text, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)

@router.callback_query(F.data == "deposit")
async def show_deposit_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.username or callback.from_user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)
    lang = user_languages.get(user_id, "english")
    if lang == "russian":
        deposit_text = (
            "💸 <b>Пополнить счет:</b>\n\n"
            "🦋 <b>CryptoBot</b> — (2.9%)\n"
            f"💰 <b>Ваш баланс:</b> ${user_data['balance']}\n\n"
            "<u>ℹ️ Мин.: $0.3 Макс.: $10,000.</u>\n"
        )
    else:
        deposit_text = (
            "💸 <b>Deposit Funds:</b>\n\n"
            "🦋 <b>CryptoBot</b> — (2.9%)\n"
            f"💰 <b>Your Balance:</b> ${user_data['balance']}\n\n"
            "<u>ℹ️ Мин.: $0.3 Макс.: $10,000.</u>\n"
        )
    await callback.message.edit_text(
        text=deposit_text,
        reply_markup=deposit_payment_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "crypto_bot")
async def choose_crypto_amount(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_name = callback.from_user.username or callback.from_user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)
    lang = user_languages.get(user_id, "english")
    if lang == "russian":
        deposit_text = (
            "💸 <b>Введите сумму пополнения:</b>\n\n"
            "🦋 <b>CryptoBot</b> — (2.9%)\n"
            f"💰 <b>Ваш баланс:</b> ${user_data['balance']}\n\n"
            "<u>ℹ️ Мин.: $0.3 Макс.: $10,000.</u>\n\n"
        )
    else:
        deposit_text = (
            "💸 <b>Enter Deposit Amount:</b>\n"
            "🦋 <b>CryptoBot</b> — (2.9%)\n"
            f"💰 <b>Your Balance:</b> ${user_data['balance']}\n\n"
            "<u>ℹ️ Min.: $0.3 Max.: $10,000.</u>\n\n"
        )
    await callback.message.edit_text(
        reply_markup=payments_keyboard(),
        text=deposit_text,
        parse_mode="HTML"
    )
    await state.set_state(DepositStates.waiting_for_amount)
    await state.update_data(user_id=user_id, lang=lang)
    await callback.answer()

@router.message(DepositStates.waiting_for_amount)
async def process_manual_amount(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    lang = user_data.get("lang", "english")
    amount_str = message.text.strip()
    try:
        amount = float(amount_str)
        if not (0.1 <= amount <= 10000):
            raise ValueError("Amount out of range")
    except ValueError:
        error_text = "Неверная сумма. Пожалуйста, введите число от 0.1 до 10,000." if lang == "russian" else "Invalid amount. Please enter a number between 0.1 and 10,000."
        await message.answer(error_text)
        return
    try:
        invoice = cryptopay_api.create_invoice(amount=amount)
        pay_url = invoice.get("result", {}).get("pay_url")
        invoice_id = invoice.get("result", {}).get("invoice_id")
        if not pay_url or not invoice_id:
            raise Exception("Не удалось получить ссылку или ID платежа")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Оплатить" if lang == "russian" else "💰 Pay", url=pay_url)]
        ])
        payment_text = (
            f"💸 Пополнение на сумму {amount:.2f} USDT\n"
            "⌛ Платеж действует 5 минут. Пожалуйста, оплатите по ссылке ниже."
        ) if lang == "russian" else (
            f"💸 Deposit of {amount:.2f} USDT\n"
            "⌛ Payment is valid for 5 minutes. Please pay using the link below."
        )
        await message.answer(
            text=payment_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        await asyncio.create_task(wait_for_payment(message, invoice_id, CRYPTO_PAY_TOKEN, amount, lang))
    except Exception as e:
        error_text = f"Ошибка при создании платежа: {e}" if lang == "russian" else f"Error creating payment: {e}"
        await message.answer(error_text)
    finally:
        await state.clear()

@router.callback_query(F.data.startswith("amounts_"))
async def process_amount_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_name = callback.from_user.username or callback.from_user.first_name
    lang = user_languages.get(user_id, "english")
    add_user_if_not_exists(user_id, user_name)
    amount_str = callback.data.split("_")[1]
    try:
        amount = float(amount_str)
        if not (0.1 <= amount <= 10000):
            raise ValueError("Amount out of range")
    except ValueError:
        error_text = "Неверная сумма" if lang == "russian" else "Invalid amount"
        await callback.answer(error_text, show_alert=True)
        return
    try:
        invoice = cryptopay_api.create_invoice(amount=amount)
        pay_url = invoice.get("result", {}).get("pay_url")
        invoice_id = invoice.get("result", {}).get("invoice_id")
        if not pay_url or not invoice_id:
            raise Exception("Не удалось получить ссылку или ID платежа")
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💰 Оплатить" if lang == "russian" else "💰 Pay", url=pay_url)]
        ])
        payment_text = (
            f"💸 Пополнение на сумму {amount:.2f} USDT\n"
            "⌛ Платеж действует 5 минут. Пожалуйста, оплатите по ссылке ниже."
        ) if lang == "russian" else (
            f"💸 Deposit of {amount:.2f} USDT\n"
            "⌛ Payment is valid for 5 minutes. Please pay using the link below."
        )
        await callback.message.edit_text(
            text=payment_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        await asyncio.create_task(wait_for_payment(callback.message, invoice_id, CRYPTO_PAY_TOKEN, amount, lang))
    except Exception as e:
        error_text = f"Ошибка при создании платежа: {e}" if lang == "russian" else f"Error creating payment: {e}"
        await callback.answer(error_text, show_alert=True)

class CryptoPayAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://pay.crypt.bot/api"

    async def make_request(self, method: str, endpoint: str, params: dict = None):
        headers = {
            "Crypto-Pay-API-Token": self.api_key,
            "Content-Type": "application/json"
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            url = f"{self.base_url}/{endpoint}"
            try:
                async with session.request(method, url, json=params) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status {response.status}: {await response.text()}")
                    return await response.json()
            except Exception as e:
                raise Exception(f"API request failed: {e}")

    async def create_invoice(self, amount: float):
        params = {
            "amount": f"{amount:.2f}",
            "asset": "USDT",
            "allow_anonymous": True
        }
        result = await self.make_request("POST", "createInvoice", params)
        return result

    async def get_invoice_status(self, invoice_id: str):
        params = {"invoice_ids": invoice_id}
        result = await self.make_request("GET", "getInvoices", params)
        if result.get("result") and len(result["result"]["items"]) > 0:
            return result["result"]["items"][0].get("status")
        return None

    async def get_balance(self):
        return await self.make_request("GET", "getBalance")

    async def get_exchange_rates(self):
        return await self.make_request("GET", "getExchangeRates")

async def check_invoice_paid(invoice_id: str, api_key: str) -> bool:
    cryptopay_api = CryptoPayAPI(api_key)
    status = await cryptopay_api.get_invoice_status(invoice_id)
    return status == "paid"

async def wait_for_payment(message: Message, invoice_id: str, api_key: str, amount: float, lang: str):
    checks = 50
    delay = 6
    for _ in range(checks):
        paid = await check_invoice_paid(invoice_id, api_key)
        if paid:
            try:
                conn = sqlite3.connect("users.db")
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                    (amount, message.from_user.id)
                )
                conn.commit()
                conn.close()
                msg = "✅ Оплата успешно получена! 💸" if lang == "russian" else "✅ Payment received successfully!"
                await message.answer(msg)
            except Exception as e:
                await message.answer(f"❌ Ошибка при обновлении баланса: {e}")
            return
        await asyncio.sleep(delay)
    timeout_msg = "⌛ Время на оплату истекло или оплата не была завершена." if lang == "russian" else "⌛ Payment time expired or was not completed."
    await message.answer(timeout_msg)

@router.callback_query(F.data == "withdraw")
async def show_withdraw_main_menu(callback: CallbackQuery):
    withdraw_text = (
        "💸 <b>Вывести средства:</b>\n\n"
        "💰 <b>Ваш баланс:</b> ${user_data['balance']}\n"
        "<u>ℹ️ Мин.: $0.3 Макс.: $10,000.</u>\n"
    )

    await callback.message.edit_text(
        text=withdraw_text,
        reply_markup=withdraw_payment_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "crypto_bot_withdraw")
async def show_crypto_withdraw_menu(callback: CallbackQuery, state: FSMContext):
    withdraws_text = (
        "💸 <b>Вывести средства:</b>\n\n"
        "💰 <b>Ваш баланс:</b> ${user_data['balance']}\n"
        "<u>ℹ️ Мин.: $0.3 Макс.: $10,000.</u>\n"
    )

    await callback.message.edit_text(
        text=withdraws_text,
        reply_markup=withdraw_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(WithdrawStates.waiting_for_amount)
    await callback.answer()

@router.callback_query(F.data.startswith("withdraw_"))
async def handle_withdraw_amount(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    try:
        amount_str = data.split("_")[1]
        amount = float(amount_str)
        user_data = get_user_data(user_id)
        balance = user_data.get("balance", 0.0)

        if balance < amount:
            await callback.message.answer(
                f"❌ Недостаточно средств. Ваш баланс: ${balance:.2f}"
            )
            return

        logging.info(f"Пользователь {user_id} запросил вывод {amount} USDT")

        result = await withdraw_funds(
            user_id=user_id,
            amount=amount,
            currency="USDT"
        )

        if result.get("ok", False):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                    (amount, user_id)
                )
                conn.commit()
                conn.close()
                logging.info(f"У пользователя {user_id} списано {amount} USDT")
                await callback.message.answer(f"✅ Успешно выведено {amount:.2f} USDT.")
            except Exception as db_error:
                logging.error(f"Ошибка базы данных: {db_error}", exc_info=True)
                await callback.message.answer("⚠️ Средства выведены, но баланс не обновлён.")
        else:
            err_msg = result.get("description", "Неизвестная ошибка")
            await callback.message.answer(f"❌ Ошибка при выводе: {err_msg}")

    except ValueError:
        await callback.message.answer("❌ Неверная сумма.")
    except Exception as e:
        logging.exception("Ошибка при обработке вывода")
        await callback.message.answer(f"❌ Ошибка: {e}")

async def withdraw_funds(user_id: int, amount: float, currency: str):
    spend_id = str(uuid.uuid4())
    user_id_str = str(user_id)
    asset_upper = currency.upper()
    logging.info(f"Инициализация transfer: user_id={user_id_str}, amount={amount}, asset={asset_upper}, spend_id={spend_id}")
    logging.info(f"withdraw_funds parameters - user_id: {user_id_str} (type: {type(user_id_str)}), amount: {amount} (type: {type(amount)}), asset: {asset_upper} (type: {type(asset_upper)})")
    try:
        transfer = cryptopay_api.transfer(
            user_id=user_id_str,
            asset=asset_upper,
            amount=amount,
            spend_id=spend_id,
            disable_send_notification=False
        )
        logging.info(f"Ответ transfer: {transfer}")
        return transfer
    except Exception as e:
        logging.exception(f"Ошибка transfer: {e}")
        return {"ok": False, "description": str(e)}

@router.message(WithdrawStates.waiting_for_amount)
async def process_custom_withdraw_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    amount_str = message.text.strip()

    try:
        amount = float(amount_str)
        if not (0.3 <= amount <= 10000):
            raise ValueError("Недопустимая сумма")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            await message.answer("❌ Пользователь не найден в базе данных.")
            return

        balance = row[0]
        if balance < amount:
            await message.answer(f"❌ Недостаточно средств. Ваш баланс: ${balance:.2f}")
            return

        result = await withdraw_funds(
            user_id=user_id,
            amount=amount,
            currency="USDT"
        )

        if result.get("ok", False):
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
                conn.commit()
                conn.close()
                await message.answer(f"✅ Успешно выведено {amount:.2f} USDT.")
            except Exception as db_error:
                logging.error(f"Ошибка базы данных: {db_error}", exc_info=True)
                await message.answer("⚠️ Средства выведены, но баланс не обновлён.")
        else:
            err_msg = result.get("description", "Неизвестная ошибка")
            await message.answer(f"❌ Ошибка при выводе: {err_msg}")

    except ValueError:
        await message.answer("❌ Введите сумму от 0.3 до 10000.")
    except Exception as e:
        logging.exception("Ошибка при обработке ручного вывода")
        await message.answer(f"❌ Произошла ошибка: {e}")
    finally:
        await state.clear()

@router.callback_query(F.data == "back")
async def back_to_home(callback: CallbackQuery):
    user = callback.from_user
    lang = user_languages.get(user.id, "russian")
    await callback.message.delete()
    await send_language_welcome(callback.message, user, lang)
    await callback.answer()

@router.callback_query(F.data == "invite_friend")
async def invite_friend_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    ref_count = count_ref(user_id)
    ref_earnings = refka_cheks_money(user_id)

    text = (
        f"<b>📎 Ваша реферальная ссылка:</b>\n"
        f"https://t.me/{NAME_CASINO}?start={user_id}\n\n"
        f"<b>👥 Количество рефералов:</b> <code>{ref_count}</code>\n"
        f"<b>💵 Заработано с рефералов:</b> <code>{ref_earnings}</code>$\n\n"
        f"<b>❓ Как работает реферальная программа:</b>\n"
        f"Вы будете получать <code>{lose_withdraw}%</code> с каждого проигрыша своего реферала.\n"
        f"Начисление происходит автоматически на ваш кошелек CryptoBot.\n\n"
        f"⚠️ <b>Минимальная ставка реферала должна составлять:</b> {min_stavka_referal}$"
    )

    await callback.message.answer(text, parse_mode="HTML", reply_markup=back())
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("top_10_"))
async def process_top_10(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = user_languages.get(user_id, "russian")
    data = callback.data

    categories = {
        "games": (
            get_top_10_games_by_users,
            "TOP-10 by Number of Games",
            "🎮 ТОП-10 по количеству игр"
        ),
        "turnover": (
            get_top_10_turnover,
            "TOP-10 by Turnover",
            "💰 ТОП-10 по обороту"
        ),
        "winnings": (
            get_top_10_winnings,
            "TOP-10 by Winnings",
            "🏆 ТОП-10 по выигрышам"
        ),
        "coefficient": (
            get_top_10_coefficient,
            "TOP-10 by Coefficient",
            "📈 ТОП-10 по коэффициенту"
        )
    }

    periods = ["all_time", "today", "week", "month"]

    selected_category = next((c for c in categories if c in data), "games")
    selected_period = next((p for p in periods if p in data), "all_time")

    category_func, category_name_en, category_name_ru = categories[selected_category]

    top_10_data = category_func(time_period=selected_period)

    if lang == "russian":
        period_text = {
            "all_time": "Всё время",
            "today": "Сегодня",
            "week": "Неделя",
            "month": "Месяц"
        }[selected_period]
        text = f"🎉 Добро пожаловать в {NAME_CASINO}! 🎲🔥\n\n{category_name_ru} ({period_text})\n➖➖➖➖➖➖➖➖\n"
        if not top_10_data:
            positions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for pos in positions:
                text += f"<blockquote>{pos} Отсутствует</blockquote>\n"
        else:
            for i, (username, value) in enumerate(top_10_data, 1):
                username = username or "Аноним"  # Handle None or empty username
                medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}️⃣"
                if selected_category == "games":
                    text += f"<blockquote>{medal} {username} — {value:,} игр</blockquote>\n"
                elif selected_category == "turnover":
                    text += f"<blockquote>{medal} {username} — ${value:,.2f}</blockquote>\n"
                elif selected_category == "winnings":
                    text += f"<blockquote>{medal} {username} — ${value:,.2f}</blockquote>\n"
                elif selected_category == "coefficient":
                    text += f"<blockquote>{medal} {username} — x{value:,.2f}</blockquote>\n"
    else:
        period_text = {
            "all_time": "All Time",
            "today": "Today",
            "week": "Week",
            "month": "Month"
        }[selected_period]
        text = f"🎉 Welcome to {NAME_CASINO}! 🎲🔥\n\n{category_name_en} ({period_text})\n➖➖➖➖➖➖➖➖\n"
        if not top_10_data:
            positions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for pos in positions:
                text += f"<blockquote>{pos} N/A</blockquote>\n"
        else:
            for i, (username, value) in enumerate(top_10_data, 1):
                username = username or "Anonymous"  # Handle None or empty username
                medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"{i}️⃣"
                if selected_category == "games":
                    text += f"<blockquote>{medal} {username} — {value:,} games</blockquote>\n"
                elif selected_category == "turnover":
                    text += f"<blockquote>{medal} {username} — ${value:,.2f}</blockquote>\n"
                elif selected_category == "winnings":
                    text += f"<blockquote>{medal} {username} — ${value:,.2f}</blockquote>\n"
                elif selected_category == "coefficient":
                    text += f"<blockquote>{medal} {username} — x{value:,.2f}</blockquote>\n"

    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=top_10_keyboard(lang=lang, selected_category=selected_category, selected_period=selected_period)
        )
    except Exception as e:
        await callback.message.answer(
            f"Ошибка: {e}" if lang == "russian" else f"Error: {e}"
        )
    finally:
        await callback.answer()


@router.callback_query(F.data == "games")
async def start_games(callback: CallbackQuery):
    video_path = "videos/games.mp4"
    if not os.path.exists(video_path):
        await callback.message.answer("Ошибка: Видео не найдено!")
        return

    video = FSInputFile(video_path)

    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    await callback.message.delete()
    await callback.message.answer_video(
        video=video,
        caption=f"💰 Баланс: {user_data['balance']}$",
        reply_markup=games(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "more_less")
async def dice_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    text = (
        f"🎲 <b>Больше/Меньше</b> — Суть игры проста: предсказание.\n"
        f"Если вы считаете, что кости покажут 4, 5 или 6 — ставьте на «Больше» 🔼.\n"
        f"Если уверены, что результат будет 1, 2 или 3 — выбирайте «Меньше» 🔽.\n\n"
        f"<blockquote>⚡️ Коэффициент: {DICE_WIN_MULTIPLIER}x от суммы ставки\n"
        f"Возможные исходы:\n"
        f"🔼 Больше — 4 / 5 / 6\n"
        f"🔽 Меньше — 1 / 2 / 3</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"💰 <b>Баланс:</b> ${user_data['balance']:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=more_less_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(DiceGameState.waiting_for_bet)

@router.callback_query(lambda c: c.data.startswith("more_less_amount_"))
async def preset_bet_amount_dice(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[3])
        if amount < 0.1 or amount > 200:
            raise ValueError("Bet amount out of range")

        user = callback.from_user
        user_id = user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < amount:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            return

        await state.update_data(bet=amount)
        await state.set_state(DiceGameState.waiting_for_choice)

        await callback.message.edit_text(
            f"🎲 <b>Больше/Меньше</b>\n\nВы поставили ${amount:.2f}. Выберите «Меньше» или «Больше»:",
            reply_markup=dice_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        logging.error(f"Invalid bet amount for user_id={callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )

@router.message(DiceGameState.waiting_for_bet)
async def process_bet_amount_dice(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Bet amount out of range")

        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await message.answer(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            return

        await state.update_data(bet=bet)
        await state.set_state(DiceGameState.waiting_for_choice)

        await message.answer(
            f"🎲 <b>Больше/Меньше</b>\n\nВы поставили ${bet:.2f}. Выберите «Меньше» или «Больше»:",
            reply_markup=dice_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        logging.error(f"Invalid bet input for user_id={message.from_user.id}: {e}")
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(lambda c: c.data in ["dice_more", "dice_less"])
async def play_dice_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        bet = data.get("bet")
        if not bet:
            await callback.message.edit_text(
                "❌ Сумма ставки не установлена. Начните заново.",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        user = callback.from_user
        user_id = user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        choice = "more" if callback.data == "dice_more" else "less"
        result_text, new_balance, winnings, result = await play_dice(
            bot=callback.bot,
            user_id=user_id,
            user=user,
            bet=bet,
            chat_id=callback.message.chat.id,
            choice=choice
        )

        await callback.message.edit_text(result_text, reply_markup=None, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        logging.error(f"Error in play_dice_handler for user_id={callback.from_user.id}: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}. Попробуйте снова.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()

@router.callback_query(F.data == "emoji_slots")
async def slots_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    text = (
        "🎰 <b>Слоты</b> - испытай удачу в классических слотах!\n\n"
        f"<blockquote>Выигрышные</blockquote>\n\n"
        "<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"💰 Баланс: {user_data['balance']}$"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=slot_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(SlotsGameState.waiting_for_bet)


@router.callback_query(F.data.startswith("slots_amount_"))
async def preset_bet_amount_slots(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError

        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.full_name or "Без имени"
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        result_text, new_balance, winnings = await play_slots(
            bot=callback.bot,
            user_id=user_id,
            user=user,
            bet=amount,
            chat_id=callback.message.chat.id
        )


        update_user_balance(user_id, new_balance)

        await callback.message.edit_text(result_text, reply_markup=None)
        await state.clear()

    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=None
        )


@router.message(SlotsGameState.waiting_for_bet)
async def process_bet_amount(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError

        user_id = message.from_user.id

        result_text, new_balance, winnings = await play_slots(
            bot=message.bot,
            user_id=user_id,
            user=message.from_user,
            bet=bet,
            chat_id=message.chat.id
        )
        update_user_balance(user_id, new_balance)

        await message.answer(result_text, reply_markup=None)
        await state.clear()

    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=None
        )

@router.callback_query(F.data == "emoji_darts")
async def darts_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    text = (
        f"🎯 <b>Дартс</b>: Проверь свою удачу в увлекательной игре!\n"
        f"Погрузись в мир дартса, где каждый бросок непредсказуем, и получай отличные выигрыши!\n\n"
        f"<blockquote>Варианты ставок:\n"
        f"• 🔴 Красное/⚪️ Белое: x{DARTS_MULTIPLIERS['red']}\n"
        f"• 🍎 Центер/❌ Мимо: x{DARTS_MULTIPLIERS['center']}</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"💰 <b>Баланс:</b> ${user_data['balance']:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=darts_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(DartsGameState.waiting_for_bet)

@router.callback_query(F.data.startswith("darts_amount_"))
async def preset_bet_amount_darts(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError

        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.full_name or "Аноним"
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < amount:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=darts_payments_keyboard()
            )
            return

        await state.update_data(bet=amount)
        await state.set_state(DartsGameState.waiting_for_choice)

        await callback.message.edit_text(
            f"🎯 <b>Дартс</b>\n\nВы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"🔴 Красное / ⚪️ Белое (x{DARTS_MULTIPLIERS['red']})\n"
            f"🍎 Центер / ❌ Мимо (x{DARTS_MULTIPLIERS['center']})",
            reply_markup=darts_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=darts_payments_keyboard()
        )

@router.message(DartsGameState.waiting_for_bet)
async def process_bet_amount_darts(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError

        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await message.answer(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=darts_payments_keyboard()
            )
            return

        await state.update_data(bet=bet)
        await state.set_state(DartsGameState.waiting_for_choice)

        await message.answer(
            f"🎯 <b>Дартс</b>\n\nВы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"🔴 Красное / ⚪️ Белое (x{DARTS_MULTIPLIERS['red']})\n"
            f"🍎 Центер / ❌ Мимо (x{DARTS_MULTIPLIERS['center']})",
            reply_markup=darts_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=darts_payments_keyboard()
        )

@router.callback_query(F.data.in_(["bet_red", "bet_white", "bet_center", "bet_miss"]))
async def play_darts_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        bet = data.get("bet")
        if not bet:
            await callback.message.edit_text(
                "❌ Сумма ставки не установлена. Начните заново.",
                reply_markup=darts_payments_keyboard()
            )
            await state.clear()
            return

        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.full_name or "Аноним"
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=darts_payments_keyboard()
            )
            await state.clear()
            return

        choice = callback.data.split("_")[1]
        result_text, new_balance, winnings, result = await play_darts(
            bot=callback.bot,
            user_id=user_id,
            user=user,
            bet=bet,
            chat_id=callback.message.chat.id,
            choice=choice
        )

        update_user_balance(user_id, new_balance)

        await callback.message.edit_text(result_text, reply_markup=None)
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}. Попробуйте снова.",
            reply_markup=darts_payments_keyboard()
        )
        await state.clear()

@router.callback_query(F.data == "emoji_football")
async def football_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    text = (
        f"⚽️ <b>Футбол</b> - ставь на гол или промах!\n\n"
        f"<blockquote>Варианты ставок:\n"
        f"• ✅ Гол: x{FOOTBALL_MULTIPLIERS['goal']}\n"
        f"• 💨 Мимо: x{FOOTBALL_MULTIPLIERS['miss']}</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"💰 <b>Баланс:</b> ${user_data['balance']:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=football_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(FootballGameState.waiting_for_bet)

@router.callback_query(F.data.startswith("football_amount_"))
async def preset_bet_amount_football(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError

        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.full_name or "Аноним"
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < amount:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=football_payments_keyboard()
            )
            return

        await state.update_data(bet=amount)
        await state.set_state(FootballGameState.waiting_for_choice)

        await callback.message.edit_text(
            f"⚽️ <b>Футбол</b>\n\nВы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"✅ Гол (x{FOOTBALL_MULTIPLIERS['goal']})\n"
            f"💨 Мимо (x{FOOTBALL_MULTIPLIERS['miss']})",
            reply_markup=football_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=football_payments_keyboard()
        )

@router.message(FootballGameState.waiting_for_bet)
async def process_bet_amount_football(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError

        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await message.answer(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=football_payments_keyboard()
            )
            return

        await state.update_data(bet=bet)
        await state.set_state(FootballGameState.waiting_for_choice)

        await message.answer(
            f"⚽️ <b>Футбол</b>\n\nВы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"✅ Гол (x{FOOTBALL_MULTIPLIERS['goal']})\n"
            f"💨 Мимо (x{FOOTBALL_MULTIPLIERS['miss']})",
            reply_markup=football_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=football_payments_keyboard()
        )

@router.callback_query(F.data.in_(["bet_goal", "bet_football_miss"]))
async def play_football_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        bet = data.get("bet")
        if not bet:
            await callback.message.edit_text(
                "❌ Сумма ставки не установлена. Начните заново.",
                reply_markup=football_payments_keyboard()
            )
            await state.clear()
            return

        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.full_name or "Аноним"
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=football_payments_keyboard()
            )
            await state.clear()
            return

        choice = callback.data.replace("bet_", "")
        result_text, new_balance, winnings, result = await play_football(
            bot=callback.bot,
            user_id=user_id,
            user=user,
            bet=bet,
            chat_id=callback.message.chat.id,
            choice=choice
        )

        update_user_balance(user_id, new_balance)

        await callback.message.edit_text(result_text, reply_markup=None)
        await state.clear()

    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}. Попробуйте снова.",
            reply_markup=football_payments_keyboard()
        )
        await state.clear()

@router.callback_query(F.data == "emoji_bowling")
async def bowling_game_instruction(callback: CallbackQuery, state: FSMContext):
    user_data = get_user_data(callback.from_user.id)
    user_balance = user_data.get("balance", 0)
    
    try:
        text = (
            f"🎳 <b>Боулинг</b> — Сбей все кегли и выиграй!\n\n"
            f"<blockquote>🎯 Варианты ставок:\n"
            f"• 🏆 Победа: x{BOWLING_MULTIPLIERS.get('win', 2.0)}\n"
            f"• 🚫 Поражение: x{BOWLING_MULTIPLIERS.get('lose', 0.0)}\n"
            f"• 🤝 Ничья: x{BOWLING_MULTIPLIERS.get('draw', 1.0)}</blockquote>\n\n"
            f"<b>Введите сумму ставки:</b>\n"
            f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
            f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
        )

        await callback.message.delete()
        await callback.message.answer(
            text=text,
            reply_markup=bowling_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(BowlingGameState.waiting_for_bet)
        await callback.answer()
    except Exception as e:
        logging.error(f"Bowling instruction error: {e}")
        await callback.answer("❌ Ошибка при запуске игры")

@router.callback_query(F.data.startswith("bowling_amount_"))
async def preset_bet_amount(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError

        await state.clear()

        await callback.message.edit_text(
            f"Вы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"🏆 Победа (x{BOWLING_MULTIPLIERS['win']})\n"
            f"🚫 Поражение (x{BOWLING_MULTIPLIERS['lose']})",
            reply_markup=bowling_choice_keyboard(amount)
        )
    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=bowling_payments_keyboard()
        )

@router.message(BowlingGameState.waiting_for_bet)
async def process_bet_amount(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError

        await state.clear()

        await message.answer(
            f"Вы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"🏆 Победа (x{BOWLING_MULTIPLIERS['win']})\n"
            f"🚫 Поражение (x{BOWLING_MULTIPLIERS['lose']})",
            reply_markup=bowling_choice_keyboard(bet)
        )
    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=bowling_payments_keyboard()
        )

@router.callback_query(F.data.startswith("bet_"))
async def process_bowling_bet(callback: CallbackQuery):
    data = callback.data.split("_")
    choice = data[1]
    bet = float(data[2])
    await callback.message.delete()
    result_caption, new_balance, winnings, result = await play_bowling(
        bot=callback.bot,
        user_id=callback.from_user.id,
        user=callback.from_user,
        bet=bet,
        chat_id=callback.message.chat.id,
        choice=choice
    )
    await callback.answer()

@router.callback_query(F.data == "emoji_hearts")
async def hearts_game_instruction(callback: CallbackQuery, state: FSMContext):
    user_data = get_user_data(callback.from_user.id)
    user_balance = user_data.get("balance", 0)
    
    text = (
        f"❣️ <b>Сердца</b> — Угадай цвет сердца и забери выигрыш!\n\n"
        f"Простая игра с коэффициентом x{HEARTS_MULTIPLIER:.1f}. Выбери цвет и испытай удачу!\n\n"
        f"<blockquote>💖 Варианты ставок:\n"
        f"• ❤️ Красное — коэф. x{HEARTS_MULTIPLIER:.1f}\n"
        f"• 💙 Синее — коэф. x{HEARTS_MULTIPLIER:.1f}</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    try:
        await callback.message.delete()
    except:
        pass
        
    await callback.message.answer(
        text=text,
        reply_markup=hearts_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(HeartsGameState.waiting_for_bet)
    await callback.answer()

@router.message(HeartsGameState.waiting_for_bet)
async def process_bet_amount_hearts(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if not 0.1 <= bet <= 200:
            raise ValueError

        await state.clear()

        await message.answer(
            f"Вы поставили ${bet:.2f}. Выберите цвет сердца:\n"
            f"❤️ Красное (x{HEARTS_MULTIPLIER:.1f})\n"
            f"💙 Синее (x{HEARTS_MULTIPLIER:.1f})",
            reply_markup=hearts_choice_keyboard(bet=bet)  # Явно указываем параметр bet
        )
    except ValueError:
        await message.answer(
            "❌ Введите корректную сумму от $0.1 до $200",
            reply_markup=hearts_payments_keyboard()
        )
        
@router.callback_query(F.data.startswith("hearts_amount_"))
async def preset_bet_amount_hearts(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if not 0.1 <= amount <= 200:
            raise ValueError

        await state.clear()

        await callback.message.edit_text(
            f"Вы поставили ${amount:.2f}. Выберите цвет сердца:\n"
            f"❤️ Красное (x{HEARTS_MULTIPLIER:.1f})\n"
            f"💙 Синее (x{HEARTS_MULTIPLIER:.1f})",
            reply_markup=hearts_choice_keyboard(bet=amount)  # Явно указываем параметр bet
        )
        await callback.answer()
    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=hearts_payments_keyboard()
        )
        await callback.answer()



@router.callback_query(F.data.startswith("hearts_"))
async def process_hearts_bet(callback: CallbackQuery):
    try:
        if not callback.data.startswith(("hearts_red_", "hearts_blue_")):
            return await callback.answer()

        data = callback.data.split("_")
        choice = data[1]  # "red" или "blue"
        bet = float(data[2])
        
        try:
            await callback.message.delete()
        except:
            pass

        result_caption, new_balance, winnings, result = await play_hearts(
            bot=callback.bot,
            user_id=callback.from_user.id,
            user=callback.from_user,
            bet=bet,
            chat_id=callback.message.chat.id,
            choice=choice
        )
        
        await callback.answer()
    except Exception as e:
        logging.error(f"Hearts game error: {e}")
        await callback.answer("❌ Ошибка в игре. Попробуйте позже.")

@router.callback_query(F.data == "emoji_basketball")
async def basketball_game_instruction(callback: CallbackQuery, state: FSMContext):
    user_data = get_user_data(callback.from_user.id)
    user_balance = user_data.get("balance", 0)
    text = (
        f"⛹️‍♂️ <b>Баскетбол</b> — Почувствуй дух игры и точность броска!\n\n"
        f"Ты на площадке, и каждый бросок решает исход игры. Сделай ставку на результат и докажи, что твоя интуиция безупречна!\n\n"
        f"<blockquote>🏀 Варианты ставок:\n"
         f"• 🏀 Гол — коэф. x{BASKETBALL_MULTIPLIERS['goal']}\n"
        f"• 💨 Мимо — коэф. x{BASKETBALL_MULTIPLIERS['miss']}\n"
        f"• ❌ Застрянет — коэф. x{BASKETBALL_MULTIPLIERS['stuck']}</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=basketball_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(BasketballGameState.waiting_for_bet)

@router.callback_query(F.data.startswith("basketball_amount_"))
async def preset_bet_amount_basketball(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError

        await state.clear()

        await callback.message.edit_text(
            f"Вы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"🏀 Гол (x{BASKETBALL_MULTIPLIERS['goal']})\n"
            f"💨 Мимо (x{BASKETBALL_MULTIPLIERS['miss']})\n"
            f"❌ Застрянет (x{BASKETBALL_MULTIPLIERS['stuck']})",
            reply_markup=basketball_choice_keyboard(amount)
        )
    except ValueError:
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=basketball_payments_keyboard()
        )

@router.message(BasketballGameState.waiting_for_bet)
async def process_bet_amount_basketball(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError

        await state.clear()

        await message.answer(
            f"Вы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"🏀 Гол (x{BASKETBALL_MULTIPLIERS['goal']})\n"
            f"💨 Мимо (x{BASKETBALL_MULTIPLIERS['miss']})\n"
            f"❌ Застрянет (x{BASKETBALL_MULTIPLIERS['stuck']})",
            reply_markup=basketball_choice_keyboard(bet)
        )
    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=basketball_payments_keyboard()
        )

@router.callback_query(F.data.startswith("basketball_"))
async def process_basketball_bet(callback: CallbackQuery):
    data = callback.data.split("_")
    choice = data[1]
    bet = float(data[2])
    await callback.message.delete()
    result_caption, new_balance, winnings, result = await play_basketball(
        bot=callback.bot,
        user_id=callback.from_user.id,
        user=callback.from_user,
        bet=bet,
        chat_id=callback.message.chat.id,
        choice=choice
    )
    await callback.answer()


@router.callback_query(F.data == "even_odd")
async def even_odd_game_instruction(callback: CallbackQuery, state: FSMContext):
    try:
        user_data = get_user_data(callback.from_user.id)
        user_balance = user_data.get("balance", 0)

        text = (
            f"🔰 <b>Чётное/Нечётное</b>\n"
            f"Попробуй угадать, будет ли выпавшее число на кубике чётным или нечётным!\n\n"
            f"<blockquote>⚡️ Коэффициент: x{EVEN_ODD_MULTIPLIER:.1f}</blockquote>\n\n"
            f"<b>Введите сумму ставки или выберите из предложенных:</b>\n"
            f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
            f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
        )

        await callback.message.answer(
            text=text,
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(EvenOddGameState.waiting_for_bet)
        await callback.answer()

        try:
            await callback.message.delete()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to delete previous message for user_id={callback.from_user.id}: {e}")

    except Exception as e:
        logging.error(f"Error in even_odd_game_instruction for user_id={callback.from_user.id}: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()

@router.callback_query(F.data.startswith("even_odd_amount_"))
async def preset_bet_amount(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[3])
        if amount < 0.1 or amount > 200:
            raise ValueError("Bet amount out of range")

        text = (
            f"Вы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"🔢 Чётное (x{EVEN_ODD_MULTIPLIER:.1f})\n"
            f"🔣 Нечётное (x{EVEN_ODD_MULTIPLIER:.1f})"
        )
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=even_odd_choice_keyboard(amount),
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            logging.warning(f"Cannot edit message for user_id={callback.from_user.id}: {e}")
            await callback.message.answer(
                text=text,
                reply_markup=even_odd_choice_keyboard(amount),
                parse_mode="HTML"
            )
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

        await callback.answer()

    except ValueError as e:
        logging.error(f"Invalid bet amount for user_id={callback.from_user.id}: {e}")
        await callback.message.answer(
            "❌ Неверная сумма. Пожалуйста, выберите сумму от $0.1 до $200.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.set_state(EvenOddGameState.waiting_for_bet)
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in preset_bet_amount for user_id={callback.from_user.id}: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()

@router.message(EvenOddGameState.waiting_for_bet)
async def process_bet_amount(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Bet amount out of range")

        text = (
            f"Вы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"🔢 Чётное (x{EVEN_ODD_MULTIPLIER:.1f})\n"
            f"🔣 Нечётное (x{EVEN_ODD_MULTIPLIER:.1f})"
        )
        await message.answer(
            text=text,
            reply_markup=even_odd_choice_keyboard(bet),
            parse_mode="HTML"
        )

    except ValueError as e:
        logging.error(f"Invalid bet input for user_id={message.from_user.id}: {e}")
        await message.answer(
            "❌ Введите корректную сумму от $0.1 до $200.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Error in process_bet_amount for user_id={message.from_user.id}: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()

@router.callback_query(F.data.startswith("even_odd_even_") | F.data.startswith("even_odd_odd_"))
async def process_even_odd_choice(callback: CallbackQuery, state: FSMContext):
    try:
        data = callback.data.split("_")
        choice = data[2]
        bet = float(data[3])

        if choice not in ["even", "odd"]:
            raise ValueError("Invalid choice")

        result_caption, new_balance, winnings, result = await play_even_odd(
            bot=callback.bot,
            user_id=callback.from_user.id,
            user=callback.from_user,
            bet=bet,
            chat_id=callback.message.chat.id,
            choice=choice
        )

        if "Ошибка" in result_caption:
            raise Exception(result_caption)

        text = (
            f"{result_caption}\n\n"
            f"<b>Сыграть еще раз?</b>"
        )
        try:
            await callback.message.edit_text(
                text=text,
                reply_markup=even_odd_payments_keyboard(),
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            logging.warning(f"Cannot edit message for user_id={callback.from_user.id}: {e}")
            await callback.message.answer(
                text=text,
                reply_markup=even_odd_payments_keyboard(),
                parse_mode="HTML"
            )
            try:
                await callback.message.delete()
            except TelegramBadRequest:
                pass

        await state.clear()
        await callback.answer()

    except ValueError as e:
        logging.error(f"Invalid input in process_even_odd_choice for user_id={callback.from_user.id}: {e}")
        await callback.message.answer(
            "❌ Неверный выбор. Выберите 'Чётное' или 'Нечётное'.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()
    except Exception as e:
        logging.error(f"Error in process_even_odd_choice for user_id={callback.from_user.id}: {e}")
        await callback.message.answer(
            f"❌ Произошла ошибка: {str(e)}. Попробуйте позже.",
            reply_markup=even_odd_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()

@router.callback_query(lambda c: c.data == "guess_number")
async def guess_number_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)

    text = (
        f"🎲 <b>Угадай число</b> — Суть игры проста: угадайте число от 1 до 6.\n"
        f"Если вы угадаете число, которое выпадет на кубике, вы выиграете!\n\n"
        f"<blockquote>⚡️ Коэффициент: {GUESS_NUMBER_MULTIPLIER}x от суммы ставки\n"
        f"Возможные исходы: 1, 2, 3, 4, 5, 6</blockquote>\n\n"
        f"<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"💰 <b>Баланс:</b> ${user_data['balance']:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=guess_number_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(GuessNumberGameState.waiting_for_bet)

@router.callback_query(F.data.startswith("guess_number_amount_"))
async def preset_bet_amount_guess_number(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[3])
        if amount < 0.1 or amount > 200:
            raise ValueError("Bet amount out of range")

        user = callback.from_user
        user_id = user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < amount:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            return

        await state.update_data(bet=amount)
        await state.set_state(GuessNumberGameState.waiting_for_number)

        await callback.message.edit_text(
            f"🎲 <b>Угадай число</b>\n\nВы поставили ${amount:.2f}. Выберите число от 1 до 6:",
            reply_markup=guess_number_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        logging.error(f"Invalid bet amount for user_id={callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )

@router.message(GuessNumberGameState.waiting_for_bet)
async def process_bet_amount_guess_number(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Bet amount out of range")

        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await message.answer(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            return

        await state.update_data(bet=bet)
        await state.set_state(GuessNumberGameState.waiting_for_number)

        await message.answer(
            f"🎲 <b>Угадай число</b>\n\nВы поставили ${bet:.2f}. Выберите число от 1 до 6:",
            reply_markup=guess_number_choice_keyboard(),
            parse_mode="HTML"
        )
    except ValueError as e:
        logging.error(f"Invalid bet input for user_id={message.from_user.id}: {e}")
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(lambda c: c.data.startswith("guess_"))
async def play_guess_number_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        bet = data.get("bet")
        if not bet:
            await callback.message.edit_text(
                "❌ Сумма ставки не установлена. Начните заново.",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        user = callback.from_user
        user_id = user.id
        user_data = get_user_data(user_id)
        balance = user_data["balance"]

        if balance < bet:
            await callback.message.edit_text(
                f"❌ Недостаточно средств! Ваш баланс: ${balance:.2f}",
                reply_markup=payments_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        guessed_number = int(callback.data.split("_")[1])
        result_text, new_balance, winnings, result = await play_guess_number(
            bot=callback.bot,
            user_id=user_id,
            user=user,
            bet=bet,
            guessed_number=guessed_number,
            chat_id=callback.message.chat.id
        )

        await callback.message.edit_text(result_text, reply_markup=None, parse_mode="HTML")
        await state.clear()

    except Exception as e:
        logging.error(f"Error in play_guess_number_handler for user_id={callback.from_user.id}: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка: {str(e)}. Попробуйте снова.",
            reply_markup=payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()


@router.callback_query(F.data == "double_dice")
async def double_dice_instruction(callback: CallbackQuery, state: FSMContext):
    user_data = get_user_data(callback.from_user.id)
    user_balance = user_data.get("balance", 0)
    text = (
        "🎲 <b>Двойной кубик</b>\n\n"
        f"<blockquote>⚡️ Коэффициент: {DOUBLE_DICE_MULTIPLIER}x от суммы ставки\n"
        "Возможные исходы:\n"
        "🔼 Два больше - чтобы победить, на обоих кубиках должно выпасть 4, 5 или 6\n"
        "🔽 Два меньше - чтобы победить, на обоих кубиках должно выпасть 1, 2 или 3\n</blockquote>\n\n"
        "<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=double_dice_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(DoubleDiceGameState.waiting_for_bet)

@router.callback_query(F.data.startswith("double_dice_amount_"))
async def preset_bet_amount(callback: CallbackQuery, state: FSMContext):
    try:
        amount = float(callback.data.split("_")[3])
        if amount < 0.1 or amount > 200:
            raise ValueError("Сумма ставки должна быть от $0.1 до $200")

        await state.update_data(bet_amount=amount)
        await state.set_state(DoubleDiceGameState.waiting_for_choice)

        await callback.message.edit_text(
            f"Вы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            "🔼 Два больше (x2.95)\n"
            "🔽 Два меньше (x2.95)",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔼 Два больше", callback_data=f"double_dice_high_{amount}"),
                    InlineKeyboardButton(text="🔽 Два меньше", callback_data=f"double_dice_low_{amount}")
                ]
            ]),
            parse_mode="HTML"
        )
    except ValueError as e:
        await callback.message.edit_text(
            f"❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=double_dice_payments_keyboard(),
            parse_mode="HTML"
        )

@router.message(DoubleDiceGameState.waiting_for_bet)
async def process_bet_amount(message: Message, state: FSMContext):
    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Сумма ставки должна быть от $0.1 до $200")

        await state.update_data(bet_amount=bet)
        await state.set_state(DoubleDiceGameState.waiting_for_choice)

        await message.answer(
            f"Вы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            "🔼 Два больше (x2.95)\n"
            "🔽 Два меньше (x2.95)",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔼 Два больше", callback_data=f"double_dice_high_{bet}"),
                    InlineKeyboardButton(text="🔽 Два меньше", callback_data=f"double_dice_low_{bet}")
                ]
            ]),
            parse_mode="HTML"
        )
    except ValueError as e:
        await message.answer(
            f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}",
            reply_markup=double_dice_payments_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("double_dice_"))
async def process_double_dice_choice(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        bet = data.get("bet_amount")
        choice = callback.data.split("_")[2]  # e.g., "high" from "double_dice_high_10.0"

        if not bet or choice not in ["high", "low"]:
            await callback.message.edit_text(
                "❌ Ошибка. Пожалуйста, начните заново.",
                reply_markup=double_dice_payments_keyboard(),
                parse_mode="HTML"
            )
            await state.clear()
            return

        result_caption, new_balance, winnings, result = await play_double_dice(
            bot=callback.bot,
            user_id=callback.from_user.id,
            user=callback.from_user,
            bet=bet,
            choice=choice,
            chat_id=callback.message.chat.id
        )

        await callback.message.delete()
        await state.clear()

    except Exception as e:
        logging.error(f"Error in process_double_dice_choice for user_id={callback.from_user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=double_dice_payments_keyboard(),
            parse_mode="HTML"
        )
        await state.clear()

@router.callback_query(F.data == "special_mines")
async def mines_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    text = (
        f"<b>РЕЖИМ: 💣 Мины</b>\n"
        f"- Открывай клетки, избегая бомб!\n"
        "Выберите сумму ставки, чтобы начать игру на поле 5x5. "
        "Каждая открытая безопасная клетка увеличивает выигрыш!\n\n"
        "<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text=text,
        reply_markup=mines_payments_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(MinesGameState.waiting_for_bet)
    await callback.answer()

@router.callback_query(F.data.startswith("mines_amount_") | (F.data == "mines_amount_stored"))
async def mines_set_bet(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)
    data = await state.get_data()
    selected_bombs = data.get("selected_bombs", 3)

    if callback.data == "mines_amount_stored":
        bet = data.get("bet")
        if bet is None or bet < 0.1 or bet > 200 or user_balance < bet:
            text = (
                f"<b>РЕЖИМ: 💣 Мины</b>\n"
                f"- Открывай клетки, избегая бомб!\n"
                "Выберите сумму ставки, чтобы начать игру на поле 5x5. "
                "Каждая открытая безопасная клетка увеличивает выигрыш!\n\n"
                "<b>Введите сумму ставки, чтобы сыграть!</b>\n"
                "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
                f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
            )
            await callback.message.edit_text(
                text=text,
                reply_markup=mines_payments_keyboard(),
                parse_mode="HTML"
            )
            await state.set_state(MinesGameState.waiting_for_bet)
            await callback.answer("⚠️ Пожалуйста, выберите сумму ставки.")
            return
    else:
        try:
            bet = float(callback.data.split("_")[2])
        except (IndexError, ValueError):
            await callback.answer("❌ Ошибка при выборе суммы", show_alert=True)
            return

        if bet < 0.1 or bet > 200:
            await callback.answer("⚠️ Сумма должна быть от $0.1 до $200", show_alert=True)
            return

        if user_balance < bet:
            await callback.answer("❌ Недостаточно средств для ставки", show_alert=True)
            return

        await state.update_data(bet=bet)
        await callback.answer(f"💵 Ставка установлена: ${bet:.2f}", show_alert=False)

    text = (
        f"<b>РЕЖИМ: 💣 Мины</b>\n"
        f"<b>Выбрано — {selected_bombs} 💣</b>\n"
        f"- Открывай клетки, избегая бомб!\n"
        "Каждая открытая безопасная клетка увеличивает выигрыш.\n\n"
        f"<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>Ставка:</b> ${bet:.2f}\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}\n\n"
        "Нажмите «Продолжить» чтобы начать игру."
    )

    try:
        current_message = callback.message.text
        current_keyboard = callback.message.reply_markup
        if (current_message == text and
            current_keyboard == mines() and
            callback.message.parse_mode == "HTML"):
            await callback.answer("Уже отображена текущая ставка")
            return
    except (AttributeError, TypeError):
        pass

    await callback.message.edit_text(
        text=text,
        reply_markup=mines(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "bomb_select")
async def bomb_select(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_bombs = data.get("selected_bombs", 3)

    coefs = MINES_COEFFICIENTS.get(selected_bombs, [])
    coef_text = " → ".join(f"x{c:.2f}" for c in coefs) or "—"

    text = (
        f"<b>РЕЖИМ: 💣 Мины</b>\n"
        f"<b>Выбрано — {selected_bombs} 💣</b>\n"
        f"Каждая безопасная клетка повышает коэффициент выигрыша.\n\n"
        f"<blockquote>{coef_text}</blockquote>\n\n"
        "Выберите количество бомб:"
    )

    new_keyboard = mines_settings_keyboard(selected_bombs)

    try:
        current_message = callback.message.text
        current_keyboard = callback.message.reply_markup
        if (current_message == text and
            current_keyboard == new_keyboard and
            callback.message.parse_mode == "HTML"):
            await callback.answer("Уже отображено текущее количество бомб")
            return
    except (AttributeError, TypeError):
        pass

    await callback.message.edit_text(
        text=text,
        reply_markup=new_keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("mines_bombs_"))
async def set_bomb_count(callback: CallbackQuery, state: FSMContext):
    try:
        bombs = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка при выборе количества бомб", show_alert=True)
        return

    data = await state.get_data()
    current_bombs = data.get("selected_bombs", 3)
    if bombs == current_bombs:
        await callback.answer(f"Уже выбрано {bombs} бомб")
        return

    await state.update_data(selected_bombs=bombs)

    coefs = MINES_COEFFICIENTS.get(bombs, [])
    coef_text = " → ".join(f"x{c:.2f}" for c in coefs) or "—"

    text = (
        f"<b>РЕЖИМ: 💣 Мины</b>\n"
        f"<b>Выбрано — {bombs} 💣</b>\n"
        f"Каждая безопасная клетка повышает коэффициент выигрыша.\n\n"
        f"<blockquote>{coef_text}</blockquote>\n\n"
        "Выберите количество бомб:"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=mines_settings_keyboard(bombs),
        parse_mode="HTML"
    )


def retry_db_operation(operation, user_id, chat_id, bot, max_retries=5, initial_retry_delay=0.1, max_delay=1.0):
    retry_delay = initial_retry_delay
    for attempt in range(max_retries):
        try:
            return operation()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_delay)
                continue
            logging.error(f"Database error in operation for user_id={user_id}: {e}")
            asyncio.create_task(bot.send_message(chat_id=chat_id, text="❌ Ошибка базы данных. Попробуйте позже."))
            raise
        except sqlite3.Error as e:
            logging.error(f"Database error in operation for user_id={user_id}: {e}")
            asyncio.create_task(bot.send_message(chat_id=chat_id, text="❌ Ошибка базы данных. Попробуйте позже."))
            raise

@router.callback_query(F.data == "play_mines")
async def play_mines(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bet = data.get("bet")
    if bet is None:
        await callback.answer("⚠️ Сначала выберите сумму ставки.", show_alert=True)
        return

    user_id = callback.from_user.id
    user = callback.from_user
    chat_id = callback.message.chat.id

    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    if "mines_field" in data:
        await callback.answer("Игра уже начата. Выберите клетку.")
        return

    if user_balance < bet:
        await callback.message.answer("❌ У вас недостаточно денег для ставки!")
        await state.clear()
        return

    retry_db_operation(
        operation=lambda: add_turnover(user_id, bet),
        user_id=user_id,
        chat_id=chat_id,
        bot=callback.bot
    )

    bomb_count = data.get("selected_bombs", 3)
    mines_field = [True] * bomb_count + [False] * (TOTAL_CELLS - bomb_count)
    random.shuffle(mines_field)
    data["mines_field"] = mines_field
    data["opened"] = []
    await state.set_data(data)

    coefs = MINES_COEFFICIENTS.get(bomb_count, [])
    coef_text = " → ".join(f"x{c:.2f}" for c in coefs)

    initial_caption = (
        f"💣 Игра «Мины» начата!\n\n"
        f"Бомб: {bomb_count}\n"
        f"<blockquote>{coef_text}</blockquote>\n"
        f"💸 Ставка: ${bet:.2f}\n"
        f"Открыто: 0 клеток\n"
        f"Текущий коэффициент: x0.00\n"
        f"Потенциальный выигрыш: $0.00"
    )
    await callback.message.delete()
    await callback.bot.send_message(chat_id=chat_id, text=initial_caption, reply_markup=generate_mine_grid(), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("mine_cell_"))
async def mine_open_cell(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if "mines_field" not in data:
        await callback.answer("Игра не начата")
        return

    try:
        cell = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.answer("❌ Ошибка")
        return

    opened = data["opened"]
    if cell in opened:
        await callback.answer("Клетка уже открыта")
        return

    opened.append(cell)
    data["opened"] = opened
    await state.set_data(data)

    mines_field = data["mines_field"]
    bomb_count = data.get("selected_bombs", 3)
    bet = data.get("bet")
    coefs = MINES_COEFFICIENTS.get(bomb_count, [])
    current_step = len(opened)
    coef = coefs[min(current_step - 1, len(coefs) - 1)] if coefs else 0.0
    potential = round(bet * coef, 2)

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id

    if mines_field[cell]:
        user_balance = get_user_data(user_id).get("balance", 0)
        new_balance = round(user_balance - bet, 2)

        conn = sqlite3.connect("users.db", timeout=10)
        try:
            retry_db_operation(
                operation=lambda: add_game_played(user_id),
                user_id=user_id,
                chat_id=chat_id,
                bot=callback.bot
            )
            retry_db_operation(
                operation=lambda: add_coefficient(user_id, 0.0),
                user_id=user_id,
                chat_id=chat_id,
                bot=callback.bot
            )
            retry_db_operation(
                operation=lambda: update_user_balance(user_id, new_balance),
                user_id=user_id,
                chat_id=chat_id,
                bot=callback.bot
            )
        finally:
            conn.close()

        await send_mines_log(callback.bot, user_id, callback.from_user, bet, False, 0, bomb_count)
        await state.clear()

        photo = FSInputFile("photo/lose.jpg")
        caption = (
            f"🚫 Проигрыш...\n"
            f"Вы наткнулись на бомбу после {current_step - 1} открытий.\n"
            f"💰 Ваш Баланс: ${new_balance:.2f}"
        )
        await callback.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="HTML")
        await callback.message.delete()

    else:
        if len(opened) == TOTAL_CELLS - bomb_count:
            user_balance = get_user_data(user_id).get("balance", 0)
            winnings = potential
            new_balance = round(user_balance - bet + winnings, 2)

            conn = sqlite3.connect("users.db", timeout=10)
            try:
                retry_db_operation(
                    operation=lambda: add_game_played(user_id),
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=callback.bot
                )
                retry_db_operation(
                    operation=lambda: add_coefficient(user_id, coef),
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=callback.bot
                )
                if winnings > 0:
                    retry_db_operation(
                        operation=lambda: add_winning(user_id, winnings),
                        user_id=user_id,
                        chat_id=chat_id,
                        bot=callback.bot
                    )
                retry_db_operation(
                    operation=lambda: update_user_balance(user_id, new_balance),
                    user_id=user_id,
                    chat_id=chat_id,
                    bot=callback.bot
                )
            finally:
                conn.close()

            await send_mines_log(callback.bot, user_id, callback.from_user, bet, True, winnings, bomb_count)
            await state.clear()

            photo = FSInputFile("photo/win.jpg")
            caption = (
                f"🏆 Победа! Все безопасные клетки открыты.\n"
                f"💰 Выигрыш: ${winnings:.2f}\n"
                f"💰 Ваш Баланс: ${new_balance:.2f}"
            )
            await callback.bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, parse_mode="HTML")
            await callback.message.delete()
        else:
            coef_text = " → ".join(f"x{c:.2f}" for c in coefs)
            caption = (
                f"✅ Безопасно!\n\n"
                f"Бомб: {bomb_count}\n"
                f"<blockquote>{coef_text}</blockquote>\n"
                f"💸 Ставка: ${bet:.2f}\n"
                f"Открыто: {current_step} клеток\n"
                f"Текущий коэффициент: x{coef:.2f}\n"
                f"Потенциальный выигрыш: ${potential:.2f}"
            )
            await callback.message.edit_text(
                text=caption,
                reply_markup=generate_mine_grid(opened=opened, current_coef=coef),
                parse_mode="HTML"
            )

    await callback.answer()

@router.callback_query(F.data == "mine_cashout")
async def mine_cashout(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if "mines_field" not in data:
        await callback.answer("Игра не начата")
        return

    bomb_count = data.get("selected_bombs", 3)
    bet = data.get("bet")
    opened = data.get("opened", [])
    current_step = len(opened)
    coefs = MINES_COEFFICIENTS.get(bomb_count, [])
    coef = coefs[min(current_step - 1, len(coefs) - 1)] if coefs and current_step > 0 else 0.0
    winnings = round(bet * coef, 2)

    user_id = callback.from_user.id
    user_balance = get_user_data(user_id).get("balance", 0)
    new_balance = round(user_balance - bet + winnings, 2)

    conn = sqlite3.connect("users.db", timeout=10)
    try:
        retry_db_operation(
            operation=lambda: add_game_played(user_id),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
        retry_db_operation(
            operation=lambda: add_coefficient(user_id, coef),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
        if winnings > 0:
            retry_db_operation(
                operation=lambda: add_winning(user_id, winnings),
                user_id=user_id,
                chat_id=callback.message.chat.id,
                bot=callback.bot
            )
        retry_db_operation(
            operation=lambda: update_user_balance(user_id, new_balance),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
    finally:
        conn.close()

    await send_mines_log(callback.bot, user_id, callback.from_user, bet, winnings > 0, winnings, bomb_count)
    await state.clear()

    photo = FSInputFile("photo/win.jpg") if winnings > 0 else FSInputFile("photo/lose.jpg")
    caption = (
        f"🏆 Вы забрали выигрыш!\n"
        f"💰 Выигрыш: ${winnings:.2f}\n"
        f"💰 Ваш Баланс: ${new_balance:.2f}"
    ) if winnings > 0 else (
        f"Вы забрали $0.00\n"
        f"💰 Ваш Баланс: ${new_balance:.2f}"
    )
    await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption, parse_mode="HTML")
    await callback.message.delete()
    await callback.answer()

@router.callback_query(F.data == "special_tower")
async def tower_game_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    add_user_if_not_exists(user.id, user.username or user.first_name)
    user_data = get_user_data(user.id)

    text = (
        "🗼 <b>Башня</b> - Открывай клетки, избегая мин!\n\n"
        "Выберите сумму ставки и количество мин (1–4). "
        "Каждая открытая безопасная клетка увеличивает выигрыш, "
        "но попадание на мину завершает игру с потерей ставки!\n\n"
        "<b>Введите сумму ставки или выберите из предложенных!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_data.get('balance', 0):.2f}"
    )

    await callback.message.delete()
    await callback.message.answer(
        text,
        reply_markup=special_tower_payments_keyboard(),
        parse_mode="HTML"
    )
    await state.set_state(TowerGameState.waiting_for_bet)
    await callback.answer()


@router.callback_query(F.data.startswith("special_tower_amount_"))
async def process_tower_bet(callback: CallbackQuery, state: FSMContext):
    bet = float(callback.data.split("_")[3])
    user = callback.from_user
    user_data = get_user_data(user.id)

    if bet > user_data.get('balance', 0):
        await callback.answer("Недостаточно средств!")
        return

    text = f"Вы указали сумму: ${bet:.2f}\n\nВыберите количество мин:"
    await callback.message.edit_text(
        text,
        reply_markup=await get_tower_keyboard_with_state(),
    )
    await state.update_data(bet=bet)
    await state.set_state(TowerGameState.waiting_for_tower_choice)
    await callback.answer()


async def get_tower_keyboard_with_state() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🗼 Башня - 1💣", callback_data="start_tower_1"),
            InlineKeyboardButton(text="🗼 Башня - 2💣", callback_data="start_tower_2"),
        ],
        [
            InlineKeyboardButton(text="🗼 Башня - 3💣", callback_data="start_tower_3"),
            InlineKeyboardButton(text="🗼 Башня - 4💣", callback_data="start_tower_4"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="tower"),
        ]
    ])
    return keyboard


@router.callback_query(F.data.startswith("start_tower_"))
async def start_tower_game(callback: CallbackQuery, state: FSMContext):
    bomb_count = int(callback.data.split("_")[2])
    data = await state.get_data()
    bet = data.get("bet")
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    coefs = TOWER_COEFFICIENTS[bomb_count]
    potential = bet * coefs[0]
    max_layers = len(coefs)  # Количество слоев равно количеству коэффициентов
    mine_positions = []  # Список мин по слоям (каждый элемент - список позиций мин для слоя)

    # Генерируем фиксированные рандомные мины для всех слоев в начале игры
    for _ in range(max_layers):
        current_mine_pos = random.sample(range(0, 5), min(bomb_count, 5))  # Рандомные уникальные позиции мин
        mine_positions.append(current_mine_pos)

    text = (
        f"🗼 Игра Башня\n"
        f"💣 Мины: {bomb_count}\n"
        f"💰 Потенциальный выигрыш: ${potential:.2f}\n"
        f"💸 Ставка: ${bet:.2f}\n"
        f"Выберите клетку на 1 слое"
    )
    await callback.message.edit_text(
        text,
        reply_markup=generate_tower_grid(opened=[], bomb_count=bomb_count, current_coef=coefs[0], mine_pos=mine_positions[0])
    )
    await state.update_data(bomb_count=bomb_count, opened=[], current_layer=0, potential=potential, mine_positions=mine_positions, max_layers=max_layers)
    await state.set_state(TowerGameState.waiting_for_cell_choice)
    await callback.answer()

@router.callback_query(F.data.startswith("tower_cell_"))
async def process_tower_cell(callback: CallbackQuery, state: FSMContext):
    cell_idx = int(callback.data.split("_")[-1])  # Извлекаем индекс клетки
    data = await state.get_data()
    opened = data.get("opened", [])
    bomb_count = data.get("bomb_count")
    current_layer = data.get("current_layer", 0)
    bet = data.get("bet")
    potential = data.get("potential")
    mine_positions = data.get("mine_positions", [])  # Список фиксированных мин по слоям
    max_layers = data.get("max_layers")
    coefs = TOWER_COEFFICIENTS[bomb_count]
    current_coef = coefs[current_layer]

    # Проверяем, что клетка в текущем слое
    start_idx = current_layer * 5
    end_idx = start_idx + 4
    if start_idx <= cell_idx <= end_idx and cell_idx not in opened:
        # Открываем весь слой после выбора одной клетки
        for idx in range(start_idx, end_idx + 1):
            if idx not in opened:
                opened.append(idx)
        await state.update_data(opened=opened, last_selected=cell_idx)  # Сохраняем последнюю выбранную клетку

        # Используем предопределенные мины для текущего слоя
        current_mine_pos = mine_positions[current_layer]
        await state.update_data(mine_positions=mine_positions)  # Обновляем состояние, хотя мины уже зафиксированы

        if (cell_idx - start_idx) in current_mine_pos:  # Проверка на попадание на мину
            user_balance = get_user_data(callback.from_user.id).get("balance", 0)
            new_balance = round(user_balance - bet, 2)
            update_user_balance(callback.from_user.id, new_balance)
            await send_tower_log(callback.bot, callback.from_user.id, callback.from_user, bet, False, 0, bomb_count)
            await state.clear()
            photo = FSInputFile("photo/lose.jpg")
            caption = (
                f"🚫 Проигрыш...\n"
                f"Вы наткнулись на бомбу на слое {current_layer + 1}.\n"
                f"💰 Ваш Баланс: ${new_balance:.2f}"
            )
            await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption, parse_mode="HTML")
            await callback.message.delete()
        elif current_layer < max_layers - 1:  # Переход к следующему слою
            new_potential = round(bet * coefs[current_layer + 1], 2)
            await state.update_data(current_layer=current_layer + 1, potential=new_potential)
            caption = (
                f"🗼 Игра Башня\n"
                f"💣 Мины: {bomb_count}\n"
                f"💰 Потенциальный выигрыш: ${new_potential:.2f}\n"
                f"💸 Ставка: ${bet:.2f}\n"
                f"Открыт слой {current_layer + 2}\n"
                f"Текущий коэффициент: x{coefs[current_layer + 1]:.2f}\n"
                f"Выберите клетку на слое {current_layer + 2}"
            )
            await callback.message.edit_text(
                text=caption,
                reply_markup=generate_tower_grid(opened=opened, bomb_count=bomb_count, current_coef=coefs[current_layer + 1], mine_pos=mine_positions[current_layer + 1], last_selected=cell_idx)
            )
        else:  # Последний слой завершен
            new_potential = round(bet * current_coef, 2)
            user_balance = get_user_data(callback.from_user.id).get("balance", 0)
            new_balance = round(user_balance - bet + new_potential, 2)
            update_user_balance(callback.from_user.id, new_balance)
            await send_tower_log(callback.bot, callback.from_user.id, callback.from_user, bet, True, new_potential, bomb_count)
            await state.clear()
            photo = FSInputFile("photo/win.jpg")
            caption = (
                f"🏆 Победа! Все слои открыты.\n"
                f"💰 Выигрыш: ${new_potential:.2f}\n"
                f"💰 Ваш Баланс: ${new_balance:.2f}"
            )
            await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption, parse_mode="HTML")
            await callback.message.delete()
    else:
        await callback.answer("Эта клетка недоступна или уже выбрана!")

    await callback.answer()

@router.callback_query(F.data == "tower_cashout")
async def tower_cashout(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data:
        await callback.answer("Игра не начата")
        return

    bomb_count = data.get("bomb_count")
    bet = data.get("bet")
    current_layer = data.get("current_layer", 0)
    coefs = TOWER_COEFFICIENTS[bomb_count]
    coef = coefs[current_layer] if current_layer < len(coefs) else coefs[-1]
    winnings = round(bet * coef, 2)

    user_id = callback.from_user.id
    user_balance = get_user_data(user_id).get("balance", 0)
    new_balance = round(user_balance - bet + winnings, 2)

    conn = sqlite3.connect("users.db", timeout=10)
    try:
        retry_db_operation(
            operation=lambda: add_game_played(user_id),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
        retry_db_operation(
            operation=lambda: add_coefficient(user_id, coef),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
        if winnings > 0:
            retry_db_operation(
                operation=lambda: add_winning(user_id, winnings),
                user_id=user_id,
                chat_id=callback.message.chat.id,
                bot=callback.bot
            )
        retry_db_operation(
            operation=lambda: update_user_balance(user_id, new_balance),
            user_id=user_id,
            chat_id=callback.message.chat.id,
            bot=callback.bot
        )
    finally:
        conn.close()

    await send_tower_log(callback.bot, user_id, callback.from_user, bet, winnings > 0, winnings, bomb_count)
    await state.clear()

    photo = FSInputFile("photo/win.jpg") if winnings > 0 else FSInputFile("photo/lose.jpg")
    caption = (
        f"🏆 Вы забрали выигрыш!\n"
        f"💰 Выигрыш: ${winnings:.2f}\n"
        f"💰 Ваш Баланс: ${new_balance:.2f}"
    ) if winnings > 0 else (
        f"Вы забрали $0.00\n"
        f"💰 Ваш Баланс: ${new_balance:.2f}"
    )
    await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo, caption=caption, parse_mode="HTML")
    await callback.message.delete()
    await callback.answer()

@router.callback_query(lambda c: c.data == "special_rps")
async def rps_game_instruction(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    # Check if balance is sufficient
    if user_balance < 0.1:
        try:
            text = "❌ Недостаточно средств на балансе! Пожалуйста, пополните баланс."
            keyboard = rps_payments_keyboard()
            current_state = await state.get_data()
            last_text = current_state.get("last_rps_text")
            last_keyboard = current_state.get("last_rps_keyboard")
            current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
            last_keyboard_str = str(last_keyboard) if last_keyboard else None

            if text != last_text or current_keyboard_str != last_keyboard_str:
                await callback.message.delete()
                await callback.message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            else:
                await callback.answer()
            await state.clear()
            await callback.answer()
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await callback.answer()
            else:
                raise
        return

    text = (
        "✂️ <b>Камень, Ножницы, Бумага</b> — Легендарная игра, где каждый ход решает все!\n\n"
        "Ты готов к дуэли? Сделай выбор и сразись с ботом! Камень, ножницы или бумага?\n\n"
        "<blockquote>🎮 Исходы:\n"
        f"• 🥇 Победа — коэф. x{RPS_MULTIPLIER:.2f}\n"
        "• 🤝 Ничья — Проигрыш</blockquote>\n\n"
        "<b>Введите сумму ставки, чтобы сыграть!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    # Get last sent text and keyboard from state
    current_state = await state.get_data()
    last_text = current_state.get("last_rps_text")
    last_keyboard = current_state.get("last_rps_keyboard")

    keyboard = rps_payments_keyboard()
    current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
    last_keyboard_str = str(last_keyboard) if last_keyboard else None

    # Only send if text or keyboard has changed
    if text != last_text or current_keyboard_str != last_keyboard_str:
        try:
            await callback.message.delete()
            await callback.message.answer(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await state.update_data(
                last_rps_text=text,
                last_rps_keyboard=keyboard.inline_keyboard
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                await callback.answer()
            else:
                raise
        except Exception as e:
            logging.error(f"Error in rps_game_instruction for user_id={user_id}: {e}")
            await callback.message.answer(
                f"❌ Произошла ошибка: {str(e)}. Попробуйте позже.",
                reply_markup=rps_payments_keyboard(),
                parse_mode="HTML"
            )
            await state.update_data(
                last_rps_text=f"❌ Произошла ошибка: {str(e)}. Попробуйте позже.",
                last_rps_keyboard=rps_payments_keyboard().inline_keyboard
            )
            await state.clear()
            return
    else:
        await callback.answer()

    await state.set_state(RPSGameState.waiting_for_bet)
    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("rps_amount_"))
async def preset_bet_amount(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        amount = float(callback.data.split("_")[2])
        if amount < 0.1 or amount > 200:
            raise ValueError("Сумма ставки должна быть от $0.1 до $200")
        if amount > user_balance:
            raise ValueError("Недостаточно средств на балансе")

        await state.update_data(bet_amount=amount)
        await state.set_state(RPSGameState.waiting_for_choice)

        text = (
            f"Вы поставили ${amount:.2f}. Выберите вариант ставки:\n"
            f"✊ Камень (x{RPS_MULTIPLIER:.2f})\n"
            f"👋 Бумага (x{RPS_MULTIPLIER:.2f})\n"
            f"✌️ Ножницы (x{RPS_MULTIPLIER:.2f})"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✊ Камень", callback_data=f"rps_rock_{amount}"),
                InlineKeyboardButton(text="👋 Бумага", callback_data=f"rps_paper_{amount}"),
                InlineKeyboardButton(text="✌️ Ножницы", callback_data=f"rps_scissors_{amount}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ])

        # Get last sent text and keyboard from state
        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await callback.answer()
                else:
                    raise
        else:
            await callback.answer()

    except ValueError as e:
        text = f"❌ Неверная сумма. Пожалуйста, выберите корректную сумму от $0.1 до $200. Ошибка: {str(e)}"
        keyboard = rps_payments_keyboard()

        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await callback.answer()
                else:
                    raise
        else:
            await callback.answer()

    await callback.answer()

@router.message(RPSGameState.waiting_for_bet)
async def process_bet_amount(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Сумма ставки должна быть от $0.1 до $200")
        if bet > user_balance:
            raise ValueError("Недостаточно средств на балансе")

        await state.update_data(bet_amount=bet)
        await state.set_state(RPSGameState.waiting_for_choice)

        text = (
            f"Вы поставили ${bet:.2f}. Выберите вариант ставки:\n"
            f"✊ Камень (x{RPS_MULTIPLIER:.2f})\n"
            f"👋 Бумага (x{RPS_MULTIPLIER:.2f})\n"
            f"✌️ Ножницы (x{RPS_MULTIPLIER:.2f})"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✊ Камень", callback_data=f"rps_rock_{bet}"),
                InlineKeyboardButton(text="👋 Бумага", callback_data=f"rps_paper_{bet}"),
                InlineKeyboardButton(text="✌️ Ножницы", callback_data=f"rps_scissors_{bet}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ])

        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await message.answer("Действие уже выполнено.")
                else:
                    raise
        else:
            await message.answer("Действие уже выполнено.")

    except ValueError as e:
        text = f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}"
        keyboard = rps_payments_keyboard()

        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await message.answer("Действие уже выполнено.")
                else:
                    raise
        else:
            await message.answer("Действие уже выполнено.")

    await message.delete()

@router.callback_query(lambda c: c.data.startswith("rps_"))
async def process_rps_choice(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        data = await state.get_data()
        bet = data.get("bet_amount")  # Corrected key
        choice = callback.data.split("_")[1]  # Corrected index for choice

        if not bet or choice not in ["rock", "paper", "scissors"]:
            text = "❌ Ошибка. Пожалуйста, начните заново."
            keyboard = rps_payments_keyboard()
            current_state = await state.get_data()
            last_text = current_state.get("last_rps_text")
            last_keyboard = current_state.get("last_rps_keyboard")
            current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
            last_keyboard_str = str(last_keyboard) if last_keyboard else None

            if text != last_text or current_keyboard_str != last_keyboard_str:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            else:
                await callback.answer()
            await state.clear()
            await callback.answer()
            return

        if bet > user_balance:
            text = "❌ Недостаточно средств на балансе. Пожалуйста, начните заново."
            keyboard = rps_payments_keyboard()
            current_state = await state.get_data()
            last_text = current_state.get("last_rps_text")
            last_keyboard = current_state.get("last_rps_keyboard")
            current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
            last_keyboard_str = str(last_keyboard) if last_keyboard else None

            if text != last_text or current_keyboard_str != last_keyboard_str:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            else:
                await callback.answer()
            await state.clear()
            await callback.answer()
            return

        result_caption, new_balance, winnings, result = await play_special_rps(
            bot=callback.bot,
            user_id=user_id,
            user=callback.from_user,
            bet=bet,
            choice=choice,
            chat_id=callback.message.chat.id
        )

        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

    except Exception as e:
        logging.error(f"Error in process_rps_choice for user_id={user_id}: {e}")
        text = "❌ Произошла ошибка. Попробуйте позже."
        keyboard = rps_payments_keyboard()
        current_state = await state.get_data()
        last_text = current_state.get("last_rps_text")
        last_keyboard = current_state.get("last_rps_keyboard")
        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_rps_text=text,
                    last_rps_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await callback.answer()
                else:
                    raise
        else:
            await callback.answer()
        await state.clear()
        await callback.answer()

@router.callback_query(F.data == "russian_roulette")
async def russian_roulette_instruction(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    user_id = user.id
    user_name = user.username or user.first_name
    add_user_if_not_exists(user_id, user_name)
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    text = (
        "🔫 <b>Русская Рулетка</b> — Проверь свою удачу в опасной игре!\n\n"
        "Выбери количество пуль и сделай ставку на свой шанс! Ощути настоящий адреналин!\n\n"
        "<blockquote>🎯 Варианты ставок:\n"
        "• 💀 1 пуля — коэф. x1.14\n"
        "• 💀 2 пули — коэф. x1.4\n"
        "• 💀 3 пули — коэф. x1.9\n"
        "• 💀 4 пули — коэф. x2.8\n"
        "• 💀 5 пуль — коэф. x5.7</blockquote>\n\n"
        "<b>Введите сумму ставки или выберите ниже, чтобы сыграть!</b>\n"
        "<blockquote>ℹ️ Мин.: $0.1 | Макс.: $200</blockquote>\n\n"
        f"<b>💰 Ваш баланс:</b> ${user_balance:.2f}"
    )

    await callback.message.delete()

    try:
        await callback.message.answer(
            text=text,
            reply_markup=russun_roulet_payments_keyboard(),
            parse_mode="HTML"
        )

        await state.set_state(RussianRouletteGameState.waiting_for_bet)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка: {str(e)}")
        raise

@router.message(RussianRouletteGameState.waiting_for_bet)
async def process_russian_roulette_bet_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        # Handle text input for custom bet amount
        bet = float(message.text.strip().replace(",", "."))
        if bet < 0.1 or bet > 200:
            raise ValueError("Сумма ставки должна быть от $0.1 до $200")
        if bet > user_balance:
            raise ValueError("Недостаточно средств на балансе")

        await state.update_data(bet_amount=bet)
        await state.set_state(RussianRouletteGameState.waiting_for_bullet_count)

        text = (
            f"Вы поставили ${bet:.2f}. Выберите количество пуль:\n"
            "• 💀 1 пуля — коэф. x1.14\n"
            "• 💀 2 пули — коэф. x1.4\n"
            "• 💀 3 пули — коэф. x1.9\n"
            "• 💀 4 пули — коэф. x2.8\n"
            "• 💀 5 пуль — коэф. x5.7"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1 пуля", callback_data=f"roulette_bullets_1_{bet}"),
                InlineKeyboardButton(text="2 пули", callback_data=f"roulette_bullets_2_{bet}"),
                InlineKeyboardButton(text="3 пули", callback_data=f"roulette_bullets_3_{bet}")
            ],
            [
                InlineKeyboardButton(text="4 пули", callback_data=f"roulette_bullets_4_{bet}"),
                InlineKeyboardButton(text="5 пуль", callback_data=f"roulette_bullets_5_{bet}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ])

        current_state = await state.get_data()
        last_text = current_state.get("last_roulette_text")
        last_keyboard = current_state.get("last_roulette_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_roulette_text=text,
                    last_roulette_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await message.answer("Действие уже выполнено.")
                else:
                    raise
        else:
            await message.answer("Действие уже выполнено.")

    except ValueError as e:
        text = f"❌ Введите корректную сумму от $0.1 до $200. Ошибка: {str(e)}"
        keyboard = russun_roulet_payments_keyboard()

        current_state = await state.get_data()
        last_text = current_state.get("last_roulette_text")
        last_keyboard = current_state.get("last_roulette_keyboard")

        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            try:
                await message.answer(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_roulette_text=text,
                    last_roulette_keyboard=keyboard.inline_keyboard
                )
            except TelegramBadRequest as e:
                if "message is not modified" in str(e):
                    await message.answer("Действие уже выполнено.")
                else:
                    raise
        else:
            await message.answer("Действие уже выполнено.")

    await message.delete()

@router.callback_query(F.data.startswith("russun_roulet_amount_"))
async def process_russian_roulette_bet_selection(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        bet = float(callback.data.replace("russun_roulet_amount_", ""))
        if bet > user_balance:
            text = "❌ Недостаточно средств на балансе. Пожалуйста, выберите другую сумму."
            keyboard = russun_roulet_payments_keyboard()
            current_state = await state.get_data()
            last_text = current_state.get("last_roulette_text")
            last_keyboard = current_state.get("last_roulette_keyboard")
            current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
            last_keyboard_str = str(last_keyboard) if last_keyboard else None

            if text != last_text or current_keyboard_str != last_keyboard_str:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                await state.update_data(
                    last_roulette_text=text,
                    last_roulette_keyboard=keyboard.inline_keyboard
                )
            await callback.answer()
            return

        await state.update_data(bet_amount=bet)
        await state.set_state(RussianRouletteGameState.waiting_for_bullet_count)

        text = (
            f"Вы поставили ${bet:.2f}. Выберите количество пуль:\n"
            "• 💀 1 пуля — коэф. x1.14\n"
            "• 💀 2 пули — коэф. x1.4\n"
            "• 💀 3 пули — коэф. x1.9\n"
            "• 💀 4 пули — коэф. x2.8\n"
            "• 💀 5 пуль — коэф. x5.7"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="1 пуля", callback_data=f"roulette_bullets_1_{bet}"),
                InlineKeyboardButton(text="2 пули", callback_data=f"roulette_bullets_2_{bet}"),
                InlineKeyboardButton(text="3 пули", callback_data=f"roulette_bullets_3_{bet}")
            ],
            [
                InlineKeyboardButton(text="4 пули", callback_data=f"roulette_bullets_4_{bet}"),
                InlineKeyboardButton(text="5 пуль", callback_data=f"roulette_bullets_5_{bet}")
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
            ]
        ])

        current_state = await state.get_data()
        last_text = current_state.get("last_roulette_text")
        last_keyboard = current_state.get("last_roulette_keyboard")
        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            await callback.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await state.update_data(
                last_roulette_text=text,
                last_roulette_keyboard=keyboard.inline_keyboard
            )
        await callback.answer()

    except Exception as e:
        logging.error(f"Error in process_russian_roulette_bet_selection for user_id={user_id}: {e}")
        text = "❌ Произошла ошибка. Попробуйте позже."
        keyboard = russun_roulet_payments_keyboard()
        current_state = await state.get_data()
        last_text = current_state.get("last_roulette_text")
        last_keyboard = current_state.get("last_roulette_keyboard")
        current_keyboard_str = str(keyboard.inline_keyboard) if keyboard else None
        last_keyboard_str = str(last_keyboard) if last_keyboard else None

        if text != last_text or current_keyboard_str != last_keyboard_str:
            await callback.message.edit_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await state.update_data(
                last_roulette_text=text,
                last_roulette_keyboard=keyboard.inline_keyboard
            )
        await state.clear()
        await callback.answer()

@router.callback_query(F.data.startswith("roulette_bullets_"))
async def process_russian_roulette_bullet_count(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    user_balance = user_data.get("balance", 0)

    try:
        data = await state.get_data()
        bet = data.get("bet_amount")
        if bet is None:
            logging.error(f"No bet_amount found in state for user_id={user_id}")
            await callback.message.answer("❌ Ошибка: Ставка не установлена. Попробуйте снова.")
            await state.clear()
            return
        try:
            bet = float(bet)
        except (TypeError, ValueError):
            logging.error(f"Invalid bet_amount format for user_id={user_id}: {bet}")
            await callback.message.answer("❌ Ошибка: Неверный формат ставки. Попробуйте снова.")
            await state.clear()
            return
        bullet_count = int(callback.data.split("_")[2])  # Extract bullet count
        logging.debug(f"Extracted bullet_count for user_id={user_id}: {bullet_count}, type={type(bullet_count)}")

        if bullet_count not in [1, 2, 3, 4, 5]:
            logging.error(f"Invalid bullet_count for user_id={user_id}: {bullet_count}")
            await callback.message.answer("❌ Неверное количество пуль. Выберите от 1 до 5.")
            await state.clear()
            return

        if bet > user_balance:
            logging.error(f"Insufficient balance for user_id={user_id}: {user_balance} < {bet}")
            await callback.message.answer("❌ У вас недостаточно денег для ставки!")
            await state.clear()
            return

        # Call play_russian_roulette and handle the return tuple
        result_tuple = await play_russian_roulette(
            bot=callback.bot,
            user_id=user_id,
            user=callback.from_user,
            bet=bet,
            bullet_count=bullet_count,
            chat_id=callback.message.chat.id
        )
        logging.debug(f"play_russian_roulette returned for user_id={user_id}: {result_tuple}")
        if not isinstance(result_tuple, tuple) or len(result_tuple) != 4:
            logging.error(f"Invalid return type from play_russian_roulette for user_id={user_id}: {type(result_tuple)}, value={result_tuple}")
            await callback.message.answer("❌ Ошибка: Неверный результат игры.")
            await state.clear()
            return
        result_caption, new_balance, winnings, result = result_tuple

        # Validate the result
        if not isinstance(result, str) or result not in ["win", "lose", "none"]:
            logging.error(f"Invalid result from play_russian_roulette for user_id={user_id}: {result}")
            await callback.message.answer("❌ Ошибка: Неверный результат игры.")
            await state.clear()
            return

        await state.clear()
        await callback.answer()

    except Exception as e:
        import traceback
        logging.error(f"Error in process_russian_roulette_bullet_count for user_id={user_id}: {e}\n{traceback.format_exc()}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")
        await state.clear()
        await callback.answer()
