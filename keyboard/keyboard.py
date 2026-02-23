from typing import List

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from config.config import *
from config import *


def language_inline_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="language_russian"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="language_english")
        ]
    ])

def start_bet_keyboard(user_id: int, lang="russian"):
    if lang == "english":
        buttons = [
            [InlineKeyboardButton(text="🚀 Games", callback_data="games")],
            [
                InlineKeyboardButton(text="🌊 Deposit", callback_data="deposit"),
                InlineKeyboardButton(text="🖨️ Withdraw", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton(text="👤 Invite a Friend", callback_data="invite_friend"),
                InlineKeyboardButton(text="🏆TOP-10", callback_data="top_10_all_time")
            ],
            [
                InlineKeyboardButton(text="Support", url=HELP_USERNAME),
                InlineKeyboardButton(text="Adapter", url=CHAT_CHANNEL)
            ],
            [
                InlineKeyboardButton(text="Add Bot to Group", url=INVITE_BOT)
            ]
        ]

        if user_id in ADMIN_LIST:
            buttons.append([InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")])

    else:
        buttons = [
            [InlineKeyboardButton(text="🚀Игры", callback_data="games")],
            [
                InlineKeyboardButton(text="🌊 Депозит", callback_data="deposit"),
                InlineKeyboardButton(text="🖨️ Вывести", callback_data="withdraw")
            ],
            [
                InlineKeyboardButton(text="👤 Пригласить друга", callback_data="invite_friend"),
                InlineKeyboardButton(text="🏆ТОП-10", callback_data="top_10_all_time")
            ],
            [
                InlineKeyboardButton(text="Поддержка", url=HELP_USERNAME),
                InlineKeyboardButton(text="Переходник", url=CHAT_CHANNEL)
            ],
            [
                InlineKeyboardButton(text="Добавить бота", url=INVITE_BOT)
            ]
        ]

        if user_id in ADMIN_LIST:
            buttons.append([InlineKeyboardButton(text="⚙️ Админ панель", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def deposit_payment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🦋 CryptoBot — (2.9%)", callback_data="crypto_bot")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
    ])

def withdraw_payment_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🦋 CryptoBot", callback_data="crypto_bot_withdraw")],
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]
])

def slot_payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="slots_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="slots_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="slots_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="slots_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="slots_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="slots_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="slots_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])

def darts_payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="darts_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="darts_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="darts_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="darts_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="darts_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="darts_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="darts_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])

def football_payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="football_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="football_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="football_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="football_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="football_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="football_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="football_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])

def bowling_payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="bowling_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="bowling_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="bowling_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="bowling_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="bowling_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="bowling_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="bowling_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])
def basketball_payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="basketball_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="basketball_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="basketball_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="basketball_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="basketball_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="basketball_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="basketball_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])

def hearts_payments_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="$1", callback_data="hearts_amount_1"),
            InlineKeyboardButton(text="$5", callback_data="hearts_amount_5"),
            InlineKeyboardButton(text="$10", callback_data="hearts_amount_10")
        ],
        [
            InlineKeyboardButton(text="$20", callback_data="hearts_amount_20"),
            InlineKeyboardButton(text="$50", callback_data="hearts_amount_50"),
            InlineKeyboardButton(text="$100", callback_data="hearts_amount_100")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def hearts_choice_keyboard(bet: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❤️ Красное", callback_data=f"hearts_red_{bet}"),
            InlineKeyboardButton(text="💙 Синее", callback_data=f"hearts_blue_{bet}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back")
        ]
    ])

def even_odd_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="even_odd_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="even_odd_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="even_odd_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="even_odd_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="even_odd_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="even_odd_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="even_odd_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def guess_number_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="guess_number_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="guess_number_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="guess_number_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="guess_number_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="guess_number_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="guess_number_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="guess_number_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def more_less_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="more_less_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="more_less_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="more_less_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="more_less_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="more_less_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="more_less_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="more_less_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])


def double_dice_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="double_dice_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="double_dice_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="double_dice_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="double_dice_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="double_dice_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="double_dice_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="double_dice_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])


def rps_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="rps_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="rps_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="rps_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="rps_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="rps_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="rps_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="rps_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def russun_roulet_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="russun_roolet_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="russun_roulet_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="russun_roulet_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="russun_roulet_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="russun_roulet_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="russun_roulet_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="russun_roulet_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def mines_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="mines_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="mines_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="mines_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="mines_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="mines_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="mines_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="mines_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def special_tower_payments_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="special_tower_amount_0.5"),
            InlineKeyboardButton(text="$1", callback_data="special_tower_amount_1"),
            InlineKeyboardButton(text="$2", callback_data="special_tower_amount_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="special_tower_amount_5"),
            InlineKeyboardButton(text="$25", callback_data="special_tower_amount_25"),
            InlineKeyboardButton(text="$50", callback_data="special_tower_amount_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="special_tower_amount_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"),
        ]
    ])

def games():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚔️ PvP-дуэли в чате", callback_data="pvp_duel")],

        [InlineKeyboardButton(text="Эмодзи игры", callback_data="ghghfhghhghffg")],

        [InlineKeyboardButton(text="🎯 Дартс", callback_data="emoji_darts"),
         InlineKeyboardButton(text="⚽️ Футбол", callback_data="emoji_football")],

        [InlineKeyboardButton(text="🎳 Боулинг", callback_data="emoji_bowling"),
         InlineKeyboardButton(text="❣️ Сердца", callback_data="emoji_hearts"),
         InlineKeyboardButton(text="🏀 Баскет", callback_data="emoji_basketball")],

        [InlineKeyboardButton(text="🎲 Больше/Меньше", callback_data="more_less"),
         InlineKeyboardButton(text="📗 Чётное/Нечётное", callback_data="even_odd")],

        [InlineKeyboardButton(text="🔢 Угадай число", callback_data="guess_number"),
         InlineKeyboardButton(text="🎲 Двойной кубик", callback_data="double_dice")],

        [InlineKeyboardButton(text="Специальные игры", callback_data="ggttgtqee33e2e")],

        [InlineKeyboardButton(text="💣 Мины", callback_data="special_mines"),
         InlineKeyboardButton(text="🗼 Башня", callback_data="special_tower"),
         InlineKeyboardButton(text="✂️ КНБ", callback_data="special_rps")],

        [InlineKeyboardButton(text="🔫 Русская Рулетка", callback_data="russian_roulette")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back")]
    ])

def payments_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="amounts_0.5"),
            InlineKeyboardButton(text="$1", callback_data="amounts_1"),
            InlineKeyboardButton(text="$2", callback_data="amounts_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="amounts_5"),
            InlineKeyboardButton(text="$25", callback_data="amounts_25"),
            InlineKeyboardButton(text="$50", callback_data="amounts_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="amounts_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ]
    ])

def withdraw_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="$0.5", callback_data="withdraw_0.5"),
            InlineKeyboardButton(text="$1", callback_data="withdraw_1"),
            InlineKeyboardButton(text="$2", callback_data="withdraw_2"),
        ],
        [
            InlineKeyboardButton(text="$5", callback_data="withdraw_5"),
            InlineKeyboardButton(text="$25", callback_data="withdraw_25"),
            InlineKeyboardButton(text="$50", callback_data="withdraw_50"),
        ],
        [
            InlineKeyboardButton(text="$100", callback_data="withdraw_100"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="withdraw"),
        ]
    ])

def back():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back"),
        ],
    ])

def top_10_keyboard(lang: str, selected_category: str, selected_period: str) -> InlineKeyboardMarkup:
    categories = {
        "games": ("🎮 Games" if lang == "english" else "🎮 Игры"),
        "turnover": ("💰 Turnover" if lang == "english" else "💰 Оборот"),
        "winnings": ("🏆 Winnings" if lang == "english" else "🏆 Выигрыши"),
        "coefficient": ("📈 Coefficient" if lang == "english" else "📈 Коэффициент")
    }
    periods = {
        "all_time": ("All Time" if lang == "english" else "Всё время"),
        "today": ("Today" if lang == "english" else "Сегодня"),
        "week": ("Week" if lang == "english" else "Неделя"),
        "month": ("Month" if lang == "english" else "Месяц")
    }

    category_buttons = [
        InlineKeyboardButton(
            text=f"✅ {name}" if key == selected_category else name,
            callback_data=f"top_10_{key}_{selected_period}"
        ) for key, name in categories.items()
    ]

    period_buttons = [
        InlineKeyboardButton(
            text=f"✅ {name}" if key == selected_period else name,
            callback_data=f"top_10_{selected_category}_{key}"
        ) for key, name in periods.items()
    ]

    back_button = InlineKeyboardButton(
        text="🔙 Back" if lang == "english" else "🔙 Назад",
        callback_data="back_to_menu"
    )

    keyboard = [
        category_buttons,
        period_buttons[:2],
        period_buttons[2:],
        [back_button]
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def mines_settings_keyboard(selected_bombs: int) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for i in range(3, 18):
        text = f"{i}{' 💣' if i == selected_bombs else ''}".strip()
        row.append(InlineKeyboardButton(text=text, callback_data=f"mines_bombs_{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="mines_amount_stored")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def generate_mine_grid(opened=None, mine_positions=None, lost=False, current_coef=None):
    opened = opened or []
    mine_positions = mine_positions or []
    keyboard_buttons = []

    for i in range(TOTAL_CELLS):
        if lost and i in mine_positions:
            label = "💥" if i in opened else "💣"
            callback_data = "ignore"
        elif i in opened:
            label = "💎"
            callback_data = "ignore"
        else:
            label = " "
            callback_data = f"mine_cell_{i}" if not lost else "ignore"

        keyboard_buttons.append(
            InlineKeyboardButton(text=label, callback_data=callback_data)
        )

    inline_keyboard = [keyboard_buttons[i:i + 5] for i in range(0, TOTAL_CELLS, 5)]

    if current_coef is not None and not lost:
        cashout_button = InlineKeyboardButton(
            text=f"Забрать x{current_coef:.2f}",
            callback_data="mine_cashout"
        )
        inline_keyboard.append([cashout_button])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def generate_tower_grid(opened: list, bomb_count: int, current_coef: float, mine_pos: list = None, last_selected: int = None) -> InlineKeyboardMarkup:
    keyboard = []
    coefs = TOWER_COEFFICIENTS[bomb_count]

    for row in range(5):
        row_buttons = []
        # Добавляем коэффициент в первую колонку, если он применим
        if row < len(coefs):
            is_interactable = row + 1 > 1 and row + 1 <= len(opened) // 5 + 1  # Делим на 5, чтобы считать слои
            callback_data = f"tower_cell_{row * 5}" if is_interactable else "ignore"  # Начало слоя
            row_buttons.append(InlineKeyboardButton(text=f"x{coefs[row]:.2f}", callback_data=callback_data))
        else:
            row_buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))  # Пустая ячейка

        # Добавляем 5 клеток грида
        for col in range(5):
            cell_idx = row * 5 + col
            if cell_idx in opened:
                if mine_pos and col in mine_pos:  # Проверяем, является ли колонка позицией мины на слое
                    label = "💣"
                elif cell_idx == last_selected:
                    label = "✅"  # Показываем галочку на последней выбранной клетке
                else:
                    label = "📦"  # Остальные открытые клетки как коробки
            else:
                label = "☁️"
            callback_data = "ignore" if cell_idx in opened else f"tower_cell_{cell_idx}"
            row_buttons.append(InlineKeyboardButton(text=label, callback_data=callback_data))
        keyboard.append(row_buttons)

    if current_coef > 0:
        keyboard.append([InlineKeyboardButton(text=f"Забрать x{current_coef:.2f}", callback_data="tower_cashout")])
    keyboard.append([InlineKeyboardButton(text="⬅️ Отмена", callback_data="tower")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
