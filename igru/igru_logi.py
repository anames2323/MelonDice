import logging
from aiogram import Bot
from aiogram.types import FSInputFile, User
from config.config import *
from database.database import get_user_level, get_user_data

async def send_hearts_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, choice: str, result: str, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = HEARTS_MULTIPLIER if win else 0.0
        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        choice_display = {"red": "❤️ Красное", "blue": "💙 Синее"}
        result_display = {"red": "❤️ Красное", "blue": "💙 Синее"}

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"❣️ <b>Сердца</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Выбор: {choice_display.get(choice, 'Неизвестно')}\n"
            f"⤷ Результат: {result_display.get(result, 'Неизвестно')}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send hearts log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для игры Сердца: {e}")

async def send_slots_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, winnings: float, combination: tuple):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = SLOTS_COMBINATIONS.get(combination, 0.0)
        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🎰 <b>Слоты</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send slots log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для слотов: {e}")


async def send_dice_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: int, choice: str, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"
        multiplier = DICE_WIN_MULTIPLIER if win else 0.0

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🎲 <b>Больше/Меньше</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send dice log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для больше/меньше: {e}")

async def send_darts_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: str, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = DARTS_MULTIPLIERS.get(result, 0.0)
        result_display = {"red": "🔴 Красное", "white": "⚪️ Белое", "center": "🍎 Центр", "miss": "❌ Мимо"}
        display_result = result_display.get(result, "Неизвестно")

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"        
            f"🎯 <b>Дартс</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send darts log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для дартс: {e}")

async def send_football_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: str, dice_value: int, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = FOOTBALL_MULTIPLIERS.get(result, 0.0)
        result_display = {"goal": "✅ Гол", "miss": "💨 Мимо"}
        display_result = result_display.get(result, "Неизвестно")

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"   
            f"⚽️ <b>Футбол</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send football log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для футбола: {e}")

async def send_bowling_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: str, user_value: int, dealer_value: int, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = BOWLING_MULTIPLIERS.get(result, 1.0 - PROCENT_DRAW / 100 if result == "draw" else 0.0)
        result_display = {"win": "🏆 Победа", "lose": "🚫 Поражение", "draw": "🤝 Ничья"}
        display_result = result_display.get(result, "Неизвестно")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"   
            f"🎳 <b>Боулинг</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"{'⤷ Комиссия за ничью: ' + str(PROCENT_DRAW) + '%' if result == 'draw' else ''}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send bowling log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для боулинга: {e}")

async def send_basketball_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: str, dice_value: int, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = BASKETBALL_MULTIPLIERS.get(result, 0.0)
        result_display = {"goal": "🏀 Гол", "miss": "💨 Мимо", "stuck": "❌ Застрянет"}
        display_result = result_display.get(result, "Неизвестно")

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"   
            f"🏀 <b>Баскетбол</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send basketball log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для баскетбола: {e}")

async def send_even_odd_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: int, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = EVEN_ODD_MULTIPLIER if win else 0.0
        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🎲 <b>Чётное/Нечётное</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send even/odd log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для чётное/нечётное: {e}")

async def send_guess_number_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: int, guessed: int, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"
        multiplier = GUESS_NUMBER_MULTIPLIER if win else 0.0

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🎲 <b>Угадай число</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.1f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send guess number log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для угадай число: {e}")

async def send_double_dice_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: tuple, choice: str, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"
        multiplier = DOUBLE_DICE_MULTIPLIER if win else 0.0
        choice_display = {
            "high": "🔼 Два больше",
            "low": "🔽 Два меньше"
        }

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🎲 <b>Двойной кубик</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.2f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send double dice log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для двойного кубика: {e}")

async def send_special_rps_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, result: tuple, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"
        multiplier = RPS_MULTIPLIER if win else 0.0

        choice_display = {
            "rock": "✊ Камень",
            "paper": "👋 Бумага",
            "scissors": "✌️ Ножницы"
        }
        emoji_display = {
            "rock": "✊",
            "paper": "👋",
            "scissors": "✌️"
        }

        user_choice, bot_choice = result
        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = f"⤷🚫 {'Ничья!' if user_choice == bot_choice else 'Проигрыш...'}"
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"✂️ <b>КНБ</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.2f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send special rps log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для Камень, Ножницы, Бумага: {e}")

async def send_russian_roulette_log(bot: Bot, user_id: int, user: User, bet: float, bullet_count: int, win: bool, winnings: float):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"
        multiplier = RUSSIAN_ROULETTE_MULTIPLIERS.get(bullet_count, 1.0)

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🔫 <b>Русская Рулетка</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.2f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send russian roulette log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для Русской Рулетки: {e}")


async def send_mines_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, winnings: float, bomb_count: int):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = winnings / bet if win and bet > 0 else 0.0

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"💣 <b>Мины</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.2f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send mines log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для мин: {e}")

async def send_tower_log(bot: Bot, user_id: int, user: User, bet: float, win: bool, winnings: float, bomb_count: int):
    try:
        user_level = get_user_level(user_id)
        user_balance = get_user_data(user_id).get("balance", 0)
        username = user.full_name or "Аноним"

        multiplier = winnings / bet if win and bet > 0 else 0.0

        if win:
            outcome = "⤷🏆 Победа!"
            photo = FSInputFile("photo/win.jpg")
        else:
            outcome = "⤷🚫 Проигрыш..."
            photo = FSInputFile("photo/lose.jpg")

        text = (
            f"👤 <b>Игрок:</b> {username}\n"
            f"⤷ <b>Уровень:</b> {user_level}\n"
            f"🗼 <b>Башня</b>\n\n"
            f"<b>Исход игры:</b>\n"
            f"{outcome}\n"
            f"⤷ Коэффициент: x{multiplier:.2f}\n"
            f"⤷ Выигрыш: ${winnings:.2f}\n"
            f"💸 <b>Ставка:</b>\n"
            f"⤷ ${bet:.2f}\n"
            f"Желаем удачи в следующих ставках! 🍀"
        )

        await bot.send_photo(chat_id=LOG_CHANNEL_ID, photo=photo, caption=text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Failed to send tower log for user_id={user_id}: {e}")
        print(f"[LOG ERROR] Не удалось отправить лог для башни: {e}")
