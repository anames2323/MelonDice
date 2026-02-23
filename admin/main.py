import asyncio
import logging
import sqlite3
import uuid
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest
from requests import RequestException
from admin.keyboard import kb_admin
from database.database import *
from keyboard.keyboard import *
from games.games import *
from games.keyboard import *
from cryptopay.cryptopay import *
from config.config import ADMIN_LIST
import os
from aiogram.types import FSInputFile

BANNER_DIR = "photo"
os.makedirs(BANNER_DIR, exist_ok=True)
cryptopay_api = CryptoPayAPI(CRYPTO_PAY_TOKEN)
user_languages = {}

class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirmation = State()

class DepositStates(StatesGroup):
    waiting_for_amount = State()

class BannerStates(StatesGroup):
    waiting_for_banner = State()
    waiting_for_banner_type = State()
    waiting_for_db_upload = State()
    waiting_for_min_bet = State()
    waiting_for_max_bet = State()
    waiting_for_admin_id = State()

class GiveMoneyStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_amount = State()

DEFAULT_MIN_BET = 0.10
DEFAULT_MAX_BET = 1000.00

logging.basicConfig(level=logging.INFO)
router = Router()

def get_level_title(param):
    pass

@router.callback_query(F.data == "admin_panel")
async def send_admin_panel(callback: CallbackQuery):
    try:
        user = callback.from_user
        user_id = user.id
        user_name = user.username or user.first_name
        lang = user_languages.get(user_id, "russian")
        user_languages[user_id] = lang

        # Add user to database, setting is_admin based on ADMIN_LIST
        add_user_if_not_exists(user_id, user_name, is_admin=1 if user_id in ADMIN_LIST else 0)

        # Check admin status: users in ADMIN_LIST are always admins, otherwise check database
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        user_data = get_user_data(user_id)

        total_usdt = 0.0
        usdt_to_usd = 0.99959757

        try:
            balance_data = await cryptopay_api.get_balance()
            rates_data = await cryptopay_api.get_exchange_rates()
            logging.info(f"Balance data: {balance_data}")
            logging.info(f"Rates data: {rates_data}")

            rates = {"USDT": 1.0}
            if rates_data and "result" in rates_data:
                for rate in rates_data["result"]:
                    if rate.get("source") == "USDT" and rate.get("target") == "USD":
                        usdt_to_usd = float(rate.get("rate", usdt_to_usd))
                    if rate.get("source") == "USDT" and rate.get("target") == "USD":
                        usd_rate = float(rate.get("rate", 0))
                        for other_rate in rates_data["result"]:
                            if other_rate.get("target") == "USD" and other_rate.get("is_crypto"):
                                rates[other_rate["source"]] = float(other_rate["rate"]) / usd_rate if usd_rate != 0 else 0

            if balance_data and "result" in balance_data:
                for item in balance_data["result"]:
                    code = item.get("currency_code")
                    available = float(item.get("available", 0))
                    onhold = float(item.get("onhold", 0))
                    total = available + onhold
                    if total > 0:
                        usdt_equiv = total * rates.get(code, 0)
                        total_usdt += usdt_equiv

        except RequestException as re:
            logging.error(f"Network error fetching balance: {re}")
            total_usdt = 0.0
        except ValueError as ve:
            logging.error(f"Data parsing error fetching balance: {ve}")
            total_usdt = 0.0
        except Exception as e:
            logging.error(f"Unexpected error fetching balance: {e}")
            total_usdt = 0.0

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM games")
            total_bets = cursor.fetchone()[0] or 0

            cursor.execute("SELECT COUNT(*), SUM(amount) FROM winnings")
            wins_result = cursor.fetchone()
            total_wins = wins_result[0] or 0
            total_wins_amount = round((wins_result[1] or 0) * usdt_to_usd, 2)

            cursor.execute("SELECT SUM(amount) FROM turnover")
            total_turnover = cursor.fetchone()[0] or 0

            total_losses = total_bets - total_wins
            total_losses_amount = round((total_turnover - (wins_result[1] or 0)) * usdt_to_usd, 2) if total_turnover else 0.0

            conn.close()

        except sqlite3.Error as db_e:
            logging.error(f"Database error fetching statistics: {db_e}")
            total_bets, total_wins, total_losses = 0, 0, 0
            total_wins_amount, total_losses_amount = 0.0, 0.0
        except Exception as e:
            logging.error(f"Unexpected error fetching statistics: {e}")
            total_bets, total_wins, total_losses = 0, 0, 0
            total_wins_amount, total_losses_amount = 0.0, 0.0

        if lang == "russian":
            text = (
                f"<b>Баланс Казны:</b>\n"
                f"<blockquote>Доступно {total_usdt:.3f} USDT</blockquote>\n\n"
                f"<b>Статистика</b>\n"
                f"<blockquote>Всего ставок: {total_bets} шт. [~ {total_turnover * usdt_to_usd:.2f}$]\n"
                f"Побед: {total_wins} шт. [~ {total_wins_amount:.2f}$]\n"
                f"Проигрышей: {total_losses} шт. [~ {total_losses_amount:.2f}$]</blockquote>\n\n"
                "<b>⚡ Информация</b>\n"
                "<blockquote>🎁 <b>В призах</b> — Это чеки которые не забрали\n"
                "победители и они еще лежат, советую не удалять до 1 дня\n"
                "💼 <b>Доступно</b> — Это сколько лежит на вашей казне.</blockquote>"
            )
        else:
            text = (
                f"<b>Treasury Balance:</b>\n"
                f"<blockquote>Available {total_usdt:.3f} USDT</blockquote>\n\n"
                f"<b>Statistics</b>\n"
                f"<blockquote>Total bets: {total_bets} pcs. [~ {total_turnover * usdt_to_usd:.2f}$]\n"
                f"Wins: {total_wins} pcs. [~ {total_wins_amount:.2f}$]\n"
                f"Losses: {total_losses} pcs. [~ {total_losses_amount:.2f}$]</blockquote>\n\n"
                "<b>⚡ Information</b>\n"
                "<blockquote>🎁 <b>On hold</b> — These are receipts that winners haven't claimed yet.\n"
                "Recommended not to delete them for up to 1 day.\n"
                "💼 <b>Available</b> — This is how much is currently in your treasury.</blockquote>"
            )

        try:
            reply_markup = kb_admin()
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
        except TelegramBadRequest as e:
            logging.warning(f"Failed to edit message: {e}")
            await callback.message.answer(text, parse_mode="HTML", reply_markup=reply_markup)
        except Exception as e:
            logging.error(f"Unexpected error editing message: {e}")
            await callback.message.answer(text, parse_mode="HTML", reply_markup=reply_markup)

        try:
            await callback.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

    except Exception as e:
        logging.error(f"Error in send_admin_panel: {e}")
        await callback.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка при открытии админ-панели.\n"
            "<i>Попробуйте снова или свяжитесь с поддержкой.</i>",
            parse_mode="HTML"
        )
        try:
            await callback.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.callback_query(lambda c: c.data == 'all_message_send')
async def process_broadcast(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        user_id = callback_query.from_user.id
        # Check admin status: users in ADMIN_LIST are always admins, otherwise check database
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        await callback_query.message.answer(
            "📢 Введите текст для рассылки всем пользователям:",
            parse_mode="HTML"
        )
        await state.set_state(BroadcastStates.waiting_for_message)
        await state.update_data(admin_id=user_id)
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")
    except Exception as e:
        logging.error(f"Error in process_broadcast: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: types.Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(broadcast_message=message.text)
        formatted_preview = (
            "📬 <b>Предпросмотр рассылки</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"{message.text}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>Подтвердите отправку или отмените действие.</i>"
        )

        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_broadcast")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_broadcast")]
        ])

        await message.answer(formatted_preview, parse_mode="HTML", reply_markup=markup)
        await state.set_state(BroadcastStates.waiting_for_confirmation)
        await message.delete()
    except Exception as e:
        logging.error(f"Error in process_broadcast_message: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await state.clear()
        await message.delete()

@router.callback_query(lambda c: c.data == 'confirm_broadcast')
async def confirm_broadcast(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    try:
        user_id = callback_query.from_user.id
        # Check admin status: users in ADMIN_LIST are always admins, otherwise check database
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        user_data = await state.get_data()
        raw_message = user_data.get("broadcast_message")
        admin_id = user_data.get("admin_id")

        formatted_message = (
            "📢 <b>Новое объявление!</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"{raw_message}\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "<i>С уважением, команда бота 🤖</i>"
        )

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id != ? AND is_admin = 0", (admin_id,))
            users = cursor.fetchall()
            conn.close()
        except Exception as e:
            await callback_query.message.answer(f"❌ Ошибка базы данных: {e}", parse_mode="HTML")
            await state.clear()
            await callback_query.message.delete()
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        success_count = 0
        failed_count = 0
        for user in users:
            try:
                if is_user_registered(user[0]):
                    await bot.send_message(user[0], formatted_message, parse_mode="HTML")
                    success_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                logging.error(f"Ошибка при отправке пользователю {user[0]}: {e}")
                failed_count += 1

        result_message = (
            "📢 <b>Рассылка завершена!</b>\n"
            f"✅ Успешно отправлено: {success_count} пользователям\n"
            f"❌ Не отправлено: {failed_count} пользователям"
        )
        await callback_query.message.answer(result_message, parse_mode="HTML")
        await callback_query.message.delete()
        await state.clear()
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

    except Exception as e:
        logging.error(f"Error in confirm_broadcast: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка при рассылке. Попробуйте снова.",
            parse_mode="HTML"
        )
        await state.clear()
        await callback_query.message.delete()
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.callback_query(lambda c: c.data == 'cancel_broadcast')
async def cancel_broadcast(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.answer("❌ Рассылка отменена.", parse_mode="HTML")
        await callback_query.message.delete()
        await state.clear()
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")
    except Exception as e:
        logging.error(f"Error in cancel_broadcast: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data == 'add_balance')
async def process_add_balance(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        # Check admin status: users in ADMIN_LIST are always admins, otherwise check database
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        await callback_query.message.answer(
            "💸 <b>Пополнение казны</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Введите сумму пополнения (от 0.1 до 10,000 USDT):\n"
            "<i>Укажите только число, например, 100.50</i>",
            parse_mode="HTML"
        )
        await state.set_state(DepositStates.waiting_for_amount)
        await state.update_data(user_id=user_id, lang="russian")
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")
    except Exception as e:
        logging.error(f"Error in process_add_balance: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.message(DepositStates.waiting_for_amount)
async def process_manual_amount(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        lang = user_data.get("lang", "russian")
        amount_str = message.text.strip().replace(',', '.')  # Handle commas as decimal separators

        try:
            amount = float(amount_str)
            if not (0.1 <= amount <= 10000):
                raise ValueError("Сумма должна быть от 0.1 до 10,000 USDT")
        except ValueError:
            error_text = (
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Пожалуйста, введите корректную сумму (например, 100.50).\n"
                "<i>Допустимый диапазон: от 0.1 до 10,000 USDT.</i>"
            ) if lang == "russian" else (
                "❌ <b>Error</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Please enter a valid amount (e.g., 100.50).\n"
                "<i>Allowed range: 0.1 to 10,000 USDT.</i>"
            )
            await message.answer(error_text, parse_mode="HTML")
            await message.delete()
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
                f"💸 <b>Пополнение на сумму {amount:.2f} USDT</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "⌛ Платеж действует 5 минут.\n"
                "<i>Оплатите по ссылке ниже.</i>"
            ) if lang == "russian" else (
                f"💸 <b>Deposit of {amount:.2f} USDT</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "⌛ Payment is valid for 5 minutes.\n"
                "<i>Please pay using the link below.</i>"
            )
            await message.answer(
                text=payment_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET deposits = deposits + ? WHERE user_id = ?", (amount, user_id))
                conn.commit()
                conn.close()
                logging.info(f"Deposits updated for user_id={user_id}, added {amount} USDT")
            except sqlite3.Error as db_error:
                logging.error(f"Database error updating deposits: {db_error}")
            await asyncio.create_task(wait_for_payment(message, invoice_id, CRYPTO_PAY_TOKEN, amount, lang))
        except Exception as e:
            error_text = (
                f"❌ <b>Ошибка при создании платежа</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"Описание: {e}\n"
                "<i>Попробуйте снова или свяжитесь с поддержкой.</i>"
            ) if lang == "russian" else (
                f"❌ <b>Error creating payment</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"Description: {e}\n"
                "<i>Please try again or contact support.</i>"
            )
            await message.answer(error_text, parse_mode="HTML")
        finally:
            await message.delete()
            await state.clear()

    except Exception as e:
        logging.error(f"Error in process_manual_amount: {e}")
        await message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data == 'edit_banners')
async def process_edit_banners(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        # Check admin status
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        # Prompt user to upload an image
        await callback_query.message.answer(
            "📷 <b>Загрузка баннера</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Пожалуйста, загрузите изображение в формате .jpg.\n"
            "<i>После загрузки вы выберете, для чего оно: победа (win.jpg) или поражение (lose.jpg). Если файл уже существует, он будет заменён.</i>",
            parse_mode="HTML"
        )
        await state.set_state(BannerStates.waiting_for_banner)
        await state.update_data(user_id=user_id)
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")
    except Exception as e:
        logging.error(f"Error in process_edit_banners: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.message(BannerStates.waiting_for_banner, F.photo)
async def process_banner_image(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in state data")

        # Check if the message contains a photo
        photo = message.photo[-1]  # Get the highest resolution photo
        file_info = await message.bot.get_file(photo.file_id)
        file_name = file_info.file_path.split("/")[-1]

        # Validate file extension
        if not file_name.lower().endswith('.jpg'):
            await message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Пожалуйста, загрузите изображение в формате .jpg.",
                parse_mode="HTML"
            )
            await message.delete()
            return

        # Store file temporarily and ask for banner type
        temp_file_path = os.path.join(BANNER_DIR, f"temp_{photo.file_id}.jpg")
        await message.bot.download(file=photo.file_id, destination=temp_file_path)

        # Create inline keyboard for selecting banner type
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏆 Победа (win.jpg)", callback_data="banner_type_win")],
            [InlineKeyboardButton(text="😔 Поражение (lose.jpg)", callback_data="banner_type_lose")],
            [InlineKeyboardButton(text="❌ Отменить", callback_data="banner_type_cancel")]
        ])

        await message.answer(
            "📷 <b>Изображение получено</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Выберите тип баннера:\n"
            "<i>Победа (win.jpg) или Поражение (lose.jpg). Если файл уже существует, он будет заменён.</i>",
            parse_mode="HTML",
            reply_markup=markup
        )
        await state.set_state(BannerStates.waiting_for_banner_type)
        await state.update_data(temp_file_path=temp_file_path)
        await message.delete()

    except Exception as e:
        logging.error(f"Error in process_banner_image: {e}", exc_info=True)
        await message.answer(
            f"❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка при загрузке баннера: {str(e)}.\n"
            "<i>Попробуйте снова.</i>",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data.startswith('banner_type_'))
async def process_banner_type(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        temp_file_path = user_data.get("temp_file_path")
        if not user_id or not temp_file_path:
            raise ValueError("User ID or temp file path not found in state data")

        banner_type = callback_query.data.split("_")[-1]
        if banner_type == "cancel":
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            await callback_query.message.answer(
                "❌ Загрузка баннера отменена.",
                parse_mode="HTML"
            )
            await callback_query.message.delete()
            await state.clear()
            return

        # Map banner type to file name
        file_name = "win.jpg" if banner_type == "win" else "lose.jpg"
        final_file_path = os.path.join(BANNER_DIR, file_name)

        # Delete existing file if it exists
        if os.path.exists(final_file_path):
            os.remove(final_file_path)
            logging.info(f"Deleted existing banner: {final_file_path}")

        if os.path.exists(temp_file_path):
            os.rename(temp_file_path, final_file_path)
        else:
            raise FileNotFoundError(f"Temporary file {temp_file_path} not found")

        await callback_query.message.answer(
            f"✅ <b>Баннер успешно загружен!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Файл сохранён как <b>{file_name}</b>.",
            parse_mode="HTML"
        )
        await callback_query.message.answer_photo(FSInputFile(final_file_path), caption=f"Предпросмотр: {file_name}")
        await callback_query.message.delete()
        await state.clear()

    except Exception as e:
        logging.error(f"Error in process_banner_type: {e}", exc_info=True)
        await callback_query.message.answer(
            f"❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка при сохранении баннера: {str(e)}.\n"
            "<i>Попробуйте снова.</i>",
            parse_mode="HTML"
        )
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        await callback_query.message.delete()
        await state.clear()

@router.message(BannerStates.waiting_for_banner)
async def process_invalid_banner(message: types.Message, state: FSMContext):
    await message.answer(
        "❌ <b>Ошибка</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Пожалуйста, отправьте изображение в формате .jpg.",
        parse_mode="HTML"
    )
    await message.delete()

@router.callback_query(lambda c: c.data == 'send_db')
async def send_database(callback_query: types.CallbackQuery, bot: Bot):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")


        db_path = "users.db"
        if not os.path.exists(db_path):
            await callback_query.message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Файл базы данных не найден.\n"
                "<i>Свяжитесь с поддержкой.</i>",
                parse_mode="HTML"
            )
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        await bot.send_document(
            chat_id=user_id,
            document=FSInputFile(db_path, filename="users.db"),
            caption="📁 База данных users.db",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

    except Exception as e:
        logging.error(f"Error in send_database: {e}", exc_info=True)

@router.callback_query(lambda c: c.data == 'load_db')
async def process_load_db(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        # Check admin status
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Failed to answer callback: {e}")
            return

        # If user is in ADMIN_LIST but not admin in database, update database
        if user_id in ADMIN_LIST and not is_admin(user_id):
            set_admin(user_id, 1)
            logging.info(f"Updated is_admin to 1 for user_id={user_id} from ADMIN_LIST")

        # Prompt user to upload a .db file
        await callback_query.message.answer(
            "📂 <b>Загрузка базы данных</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Пожалуйста, отправьте файл базы данных (.db).\n"
            "<i>Текущая база данных (users.db) будет удалена и заменена загруженным файлом.</i>",
            parse_mode="HTML"
        )
        await state.set_state(BannerStates.waiting_for_db_upload)
        await state.update_data(user_id=user_id)
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")
    except Exception as e:
        logging.error(f"Error in process_load_db: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Failed to answer callback: {e}")

@router.message(BannerStates.waiting_for_db_upload, F.document)
async def process_db_upload(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in state data")

        document = message.document
        file_name = document.file_name

        if not file_name.lower().endswith('.db'):
            await message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Пожалуйста, загрузите файл базы данных с расширением .db.",
                parse_mode="HTML"
            )
            await message.delete()
            return

        temp_file_path = os.path.join(os.path.dirname(DB_PATH), f"temp_{document.file_id}.db")
        await message.bot.download(file=document.file_id, destination=temp_file_path)

        try:
            conn = sqlite3.connect(temp_file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            if not tables:
                raise sqlite3.Error("Файл не является действительной базой данных SQLite")
        except sqlite3.Error as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            await message.answer(
                f"❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                f"Загруженный файл не является действительной базой данных SQLite: {str(e)}.\n"
                "<i>Попробуйте снова.</i>",
                parse_mode="HTML"
            )
            await message.delete()
            await state.clear()
            return

        # Delete existing database if it exists
        db_path = DB_PATH
        if os.path.exists(db_path):
            os.remove(db_path)
            logging.info(f"Deleted existing database: {db_path}")

        # Move new file to replace users.db
        if os.path.exists(temp_file_path):
            os.rename(temp_file_path, db_path)
        else:
            raise FileNotFoundError(f"Temporary file {temp_file_path} not found")

        # Confirm successful upload
        await message.answer(
            f"✅ <b>База данных успешно загружена!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Файл сохранён как <b>users.db</b>.",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

    except Exception as e:
        logging.error(f"Error in process_db_upload: {e}", exc_info=True)
        await message.answer(
            f"❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка при загрузке базы данных: {str(e)}.\n"
            "<i>Попробуйте снова.</i>",
            parse_mode="HTML"
        )
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        await message.delete()
        await state.clear()

@router.message(BannerStates.waiting_for_db_upload)
async def process_invalid_db(message: types.Message, state: FSMContext):
    await message.answer(
        "❌ <b>Ошибка</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "Пожалуйста, отправьте файл базы данных с расширением .db.",
        parse_mode="HTML"
    )
    await message.delete()

@router.callback_query(lambda c: c.data == 'edit_bet')
async def process_edit_bet_limits(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        # Проверка админа
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            await callback_query.answer()
            return

        # Текущие лимиты берем из конфига
        current_min_bet = DIAPAZONE_AMOUNT_MIN
        current_max_bet = DIAPAZONE_AMOUNT_MAX

        await callback_query.message.answer(
            f"🏛 <b>Изменение лимитов ставок</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Текущая минимальная ставка: {current_min_bet:.2f} USDT\n"
            f"Текущая максимальная ставка: {current_max_bet:.2f} USDT\n"
            f"Выберите, что изменить:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔽 Установить минимальную ставку", callback_data="set_min_bet")],
                [InlineKeyboardButton(text="🔼 Установить максимальную ставку", callback_data="set_max_bet")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
            ])
        )
        await state.update_data(user_id=user_id, min_bet_set=False)
        await callback_query.answer()

    except Exception as e:
        logging.error(f"Error in process_edit_bet_limits: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.answer()

@router.callback_query(lambda c: c.data == 'set_min_bet')
async def process_set_min_bet(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            await callback_query.answer()
            return

        current_min_bet = DIAPAZONE_AMOUNT_MIN
        await callback_query.message.answer(
            f"🏛 <b>Установка минимальной ставки</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Текущая минимальная ставка: {current_min_bet:.2f} USDT\n"
            f"Введите новую минимальную ставку (от {DIAPAZONE_AMOUNT_MIN:.2f} до {DIAPAZONE_AMOUNT_MAX:.2f} USDT):\n"
            f"<i>Укажите число, например, 2.50</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
            ])
        )
        await state.set_state(BannerStates.waiting_for_min_bet)
        await state.update_data(user_id=user_id)
        await callback_query.answer()

    except Exception as e:
        logging.error(f"Error in process_set_min_bet: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.answer()

@router.callback_query(lambda c: c.data == 'set_max_bet')
async def process_set_max_bet(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            await callback_query.answer()
            return

        user_data = await state.get_data()
        min_bet_set = user_data.get("min_bet_set", False)
        if not min_bet_set:
            await callback_query.message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Пожалуйста, сначала установите минимальную ставку.",
                parse_mode="HTML"
            )
            await callback_query.answer()
            return

        current_max_bet = DIAPAZONE_AMOUNT_MAX
        new_min_bet = user_data.get("new_min_bet", DIAPAZONE_AMOUNT_MIN)
        await callback_query.message.answer(
            f"🏛 <b>Установка максимальной ставки</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Новая минимальная ставка: {new_min_bet:.2f} USDT\n"
            f"Текущая максимальная ставка: {current_max_bet:.2f} USDT\n"
            f"Введите новую максимальную ставку (от {new_min_bet:.2f} до {DIAPAZONE_AMOUNT_MAX:.2f} USDT):\n"
            f"<i>Укажите число, например, 19.50</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
            ])
        )
        await state.set_state(BannerStates.waiting_for_max_bet)
        await callback_query.answer()

    except Exception as e:
        logging.error(f"Error in process_set_max_bet: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.answer()

@router.message(BannerStates.waiting_for_min_bet)
async def process_min_bet_input(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        if not user_id:
            raise ValueError("User ID not found in state data")

        amount_str = message.text.strip().replace(',', '.')
        try:
            new_min_bet = float(amount_str)
            if not (DIAPAZONE_AMOUNT_MIN <= new_min_bet <= DIAPAZONE_AMOUNT_MAX):
                raise ValueError()
        except:
            await message.answer(
                f"❌ <b>Ошибка</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"Пожалуйста, введите корректную сумму (например, 2.50).\n"
                f"<i>Допустимый диапазон: от {DIAPAZONE_AMOUNT_MIN:.2f} до {DIAPAZONE_AMOUNT_MAX:.2f} USDT.</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
                ])
            )
            await message.delete()
            return

        await state.update_data(new_min_bet=new_min_bet, min_bet_set=True)
        current_max_bet = DIAPAZONE_AMOUNT_MAX
        await message.answer(
            f"🏛 <b>Изменение лимитов ставок</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Новая минимальная ставка: {new_min_bet:.2f} USDT\n"
            f"Текущая максимальная ставка: {current_max_bet:.2f} USDT\n"
            f"Выберите, что изменить:",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔼 Установить максимальную ставку", callback_data="set_max_bet")],
                [InlineKeyboardButton(text="✅ Сохранить и завершить", callback_data="save_bet_limits")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
            ])
        )
        await message.delete()

    except Exception as e:
        logging.error(f"Error in process_min_bet_input: {e}")
        await message.answer(
            f"❌ <b>Ошибка</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка: {str(e)}.\n"
            f"<i>Попробуйте снова.</i>",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

@router.message(BannerStates.waiting_for_max_bet)
async def process_max_bet_input(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        user_id = user_data.get("user_id")
        new_min_bet = user_data.get("new_min_bet")
        if not user_id or new_min_bet is None:
            raise ValueError("User ID or new_min_bet not found in state data")

        amount_str = message.text.strip().replace(',', '.')
        try:
            new_max_bet = float(amount_str)
            if not (new_min_bet <= new_max_bet <= DIAPAZONE_AMOUNT_MAX):
                raise ValueError()
        except:
            await message.answer(
                f"❌ <b>Ошибка</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"Пожалуйста, введите корректную сумму (например, 19.50).\n"
                f"<i>Допустимый диапазон: от {new_min_bet:.2f} до {DIAPAZONE_AMOUNT_MAX:.2f} USDT.</i>",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_bet_limits")]
                ])
            )
            await message.delete()
            return
        await message.answer(
            f"✅ <b>Лимиты ставок обновлены!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Новая минимальная ставка: {new_min_bet:.2f} USDT\n"
            f"Новая максимальная ставка: {new_max_bet:.2f} USDT",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

    except Exception as e:
        logging.error(f"Error in process_max_bet_input: {e}")
        await message.answer(
            f"❌ <b>Ошибка</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка: {str(e)}.\n"
            f"<i>Попробуйте снова.</i>",
            parse_mode="HTML"
        )
        await message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data == 'cancel_bet_limits')
async def cancel_bet_limits(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.answer(
            "❌ Изменение лимитов ставок отменено.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()
        await callback_query.answer()
    except Exception as e:
        logging.error(f"Error in cancel_bet_limits: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()

def update_config_admin_list(admin_ids: list):
    """Обновляет ADMIN_LIST в config/config.py с указанным списком ID администраторов."""
    try:
        # Поднимаемся на один уровень от admin к корню проекта, затем к config/config.py
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.py")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Файл конфигурации не найден по пути: {config_path}")

        # Читаем содержимое config/config.py
        with open(config_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Обновляем строку ADMIN_LIST
        new_lines = []
        admin_list_updated = False
        for line in lines:
            if line.strip().startswith('ADMIN_LIST ='):
                new_line = f"ADMIN_LIST = {admin_ids}\n"
                new_lines.append(new_line)
                admin_list_updated = True
            else:
                new_lines.append(line)

        # Если ADMIN_LIST не найден, добавляем его
        if not admin_list_updated:
            new_lines.append(f"ADMIN_LIST = {admin_ids}\n")

        # Записываем обновленное содержимое в config/config.py
        with open(config_path, 'w', encoding='utf-8') as file:
            file.writelines(new_lines)

        # Перезагружаем модуль config для обновления ADMIN_LIST в памяти
        from importlib import reload
        import config.config
        reload(config.config)
        logging.info(f"Обновлен ADMIN_LIST в config/config.py: {admin_ids}")
    except FileNotFoundError as e:
        logging.error(f"Ошибка при обновлении config/config.py: {e}")
        raise Exception(f"Не удалось обновить config/config.py: {str(e)}")
    except PermissionError:
        logging.error(f"Отказано в доступе при записи в {config_path}")
        raise Exception(f"Не удалось обновить config/config.py: Отказано в доступе")
    except Exception as e:
        logging.error(f"Ошибка при обновлении config/config.py: {e}")
        raise Exception(f"Не удалось обновить config/config.py: {str(e)}")

@router.callback_query(lambda c: c.data == 'add_admin')
async def process_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Не удалось ответить на callback: {e}")
            return

        await callback_query.message.answer(
            "👑 <b>Добавление администратора</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Введите ID пользователя, которого хотите назначить администратором:\n"
            "<i>Укажите число, например, 123456789</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_add_admin")]
            ])
        )
        await state.set_state(BannerStates.waiting_for_admin_id)
        await state.update_data(admin_id=user_id, action="add_admin")
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")
    except Exception as e:
        logging.error(f"Ошибка в process_add_admin: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")

@router.callback_query(lambda c: c.data == 'remove_admin')
async def process_remove_admin(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Не удалось ответить на callback: {e}")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
        admin_count = cursor.fetchone()[0]
        conn.close()
        if admin_count <= 1 and len(ADMIN_LIST) <= 1:
            await callback_query.message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Нельзя удалить последнего администратора.\n"
                "<i>Добавьте другого администратора перед удалением.</i>",
                parse_mode="HTML"
            )
            try:
                await callback_query.answer()
            except TelegramBadRequest as e:
                logging.warning(f"Не удалось ответить на callback: {e}")
            return

        await callback_query.message.answer(
            "🗑 <b>Удаление администратора</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Введите ID пользователя, которого хотите лишить прав администратора:\n"
            "<i>Укажите число, например, 123456789</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_remove_admin")]
            ])
        )
        await state.set_state(BannerStates.waiting_for_admin_id)
        await state.update_data(admin_id=user_id, action="remove_admin")
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")
    except Exception as e:
        logging.error(f"Ошибка в process_remove_admin: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")

@router.message(BannerStates.waiting_for_admin_id)
async def process_admin_id_input(message: types.Message, state: FSMContext):
    try:
        user_data = await state.get_data()
        admin_id = user_data.get("admin_id")
        action = user_data.get("action")
        if not admin_id or not action:
            raise ValueError("Admin ID или действие не найдены в данных состояния")

        try:
            target_user_id = int(message.text.strip())
            if target_user_id <= 0:
                raise ValueError("ID пользователя должен быть положительным числом")
        except ValueError:
            await message.answer(
                "❌ <b>Ошибка</b>\n"
                "━━━━━━━━━━━━━━━━━━━━━\n"
                "Пожалуйста, введите корректный ID пользователя (например, 123456789).",
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}")]
                ])
            )
            await message.delete()
            return

        if action == "add_admin":
            if not is_user_registered(target_user_id):
                await message.answer(
                    "❌ <b>Ошибка</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "Пользователь с указанным ID не зарегистрирован в боте.\n"
                    "<i>Пользователь должен сначала взаимодействовать с ботом.</i>",
                    parse_mode="HTML",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_add_admin")]
                    ])
                )
                await message.delete()
                return

            if target_user_id in ADMIN_LIST or is_admin(target_user_id):
                await message.answer(
                    "❌ <b>Ошибка</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "Пользователь уже является администратором.",
                    parse_mode="HTML"
                )
                await message.delete()
                await state.clear()
                return

            # Сначала обновляем базу данных
            if not set_admin(target_user_id, 1):
                raise sqlite3.Error(f"Не удалось обновить статус is_admin для user_id={target_user_id}")

            # Затем обновляем config/config.py
            new_admin_list = list(ADMIN_LIST) + [target_user_id]
            update_config_admin_list(new_admin_list)

            user_data = get_user_data(target_user_id)
            user_name = user_data.get("user_name", "Unknown")
            await message.answer(
                f"✅ <b>Администратор добавлен!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"ID: {target_user_id}\n"
                f"Имя: {user_name}\n"
                f"<i>Пользователь теперь имеет права администратора.</i>",
                parse_mode="HTML"
            )

        elif action == "remove_admin":
            if target_user_id not in ADMIN_LIST and not is_admin(target_user_id):
                await message.answer(
                    "❌ <b>Ошибка</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "Пользователь не является администратором.",
                    parse_mode="HTML"
                )
                await message.delete()
                await state.clear()
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1 AND user_id != ?", (target_user_id,))
            remaining_admins = cursor.fetchone()[0]
            remaining_config_admins = len([uid for uid in ADMIN_LIST if uid != target_user_id])
            conn.close()
            if remaining_admins == 0 and remaining_config_admins == 0:
                await message.answer(
                    "❌ <b>Ошибка</b>\n"
                    "━━━━━━━━━━━━━━━━━━━━━\n"
                    "Нельзя удалить последнего администратора.\n"
                    "<i>Добавьте другого администратора перед удалением.</i>",
                    parse_mode="HTML"
                )
                await message.delete()
                await state.clear()
                return

            # Сначала обновляем config/config.py
            new_admin_list = [uid for uid in ADMIN_LIST if uid != target_user_id]
            update_config_admin_list(new_admin_list)

            # Затем обновляем базу данных
            if is_user_registered(target_user_id) and not set_admin(target_user_id, 0):
                raise sqlite3.Error(f"Не удалось обновить статус is_admin для user_id={target_user_id}")

            user_data = get_user_data(target_user_id)
            user_name = user_data.get("user_name", "Unknown")
            await message.answer(
                f"✅ <b>Администратор удалён!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"ID: {target_user_id}\n"
                f"Имя: {user_name}\n"
                f"<i>Пользователь больше не имеет прав администратора.</i>",
                parse_mode="HTML"
            )

        await message.delete()
        await state.clear()

    except Exception as e:
        logging.error(f"Ошибка в process_admin_id_input: {e}")
        await message.answer(
            f"❌ <b>Ошибка</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Произошла ошибка: {str(e)}.\n"
            f"<i>Попробуйте снова.</i>",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}")]
            ])
        )
        await message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data == 'cancel_add_admin')
async def cancel_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.answer(
            "❌ Добавление администратора отменено.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")
    except Exception as e:
        logging.error(f"Ошибка в cancel_add_admin: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()

@router.callback_query(lambda c: c.data == 'cancel_remove_admin')
async def cancel_remove_admin(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        await callback_query.message.answer(
            "❌ Удаление администратора отменено.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()
        try:
            await callback_query.answer()
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось ответить на callback: {e}")
    except Exception as e:
        logging.error(f"Ошибка в cancel_remove_admin: {e}")
        await callback_query.message.answer(
            "❌ <b>Ошибка</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Произошла ошибка. Попробуйте снова.",
            parse_mode="HTML"
        )
        await callback_query.message.delete()
        await state.clear()

@router.callback_query(F.data == 'give_money_admin')
async def process_give_money_admin(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        user_id = callback_query.from_user.id
        is_user_admin = user_id in ADMIN_LIST or is_admin(user_id)
        if not is_user_admin:
            await callback_query.message.answer("❌ Доступ запрещён.", parse_mode="HTML")
            await callback_query.answer()
            return

        await callback_query.message.answer("Введите ID пользователя, которому нужно выдать баланс:")
        await state.set_state(GiveMoneyStates.waiting_for_user_id)
        await callback_query.answer()
    except Exception as e:
        logging.error(f"Error in process_give_money_admin: {e}")
        await callback_query.message.answer("❌ Произошла ошибка при обработке запроса.")
        await callback_query.answer()

@router.message(GiveMoneyStates.waiting_for_user_id)
async def process_user_id_for_give_money(message: types.Message, state: FSMContext):
    try:
        target_user_id = int(message.text)
        if not is_user_registered(target_user_id):
            await message.answer("Пользователь с таким ID не найден в базе данных. Пожалуйста, введите корректный ID.")
            return

        await state.update_data(target_user_id=target_user_id)
        await message.answer(f"Введите сумму, которую нужно выдать пользователю {target_user_id}:")
        await state.set_state(GiveMoneyStates.waiting_for_amount)
    except ValueError:
        await message.answer("Некорректный ID пользователя. Пожалуйста, введите числовой ID.")
    except Exception as e:
        logging.error(f"Error in process_user_id_for_give_money: {e}")
        await message.answer("❌ Произошла ошибка при обработке ID пользователя.")
        await state.clear()

@router.message(GiveMoneyStates.waiting_for_amount)
async def process_amount_for_give_money(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            await message.answer("Сумма должна быть положительной. Пожалуйста, введите корректную сумму.")
            return

        user_data = await state.get_data()
        target_user_id = user_data.get('target_user_id')

        current_balance = get_user_data(target_user_id)['balance']
        new_balance = current_balance + amount
        update_user_balance(target_user_id, new_balance)

        await message.answer(f"✅ Пользователю {target_user_id} успешно выдано {amount} USDT. Новый баланс: {new_balance} USDT.")
        await state.clear()
    except ValueError:
        await message.answer("Некорректная сумма. Пожалуйста, введите числовое значение.")
    except Exception as e:
        logging.error(f"Error in process_amount_for_give_money: {e}")
        await message.answer("❌ Произошла ошибка при выдаче баланса.")
        await state.clear()