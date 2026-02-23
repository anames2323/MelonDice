import os
import sqlite3
import logging
from datetime import datetime, timedelta
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter
import time

from config.config import LEVELS

router = Router()
DB_PATH = "users.db"
user_languages = {}

def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()

    cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    user_name TEXT,
                    balance REAL DEFAULT 0.0,
                    total_turnover REAL DEFAULT 0.0,
                    deposits INTEGER DEFAULT 0,
                    withdrawals INTEGER DEFAULT 0,
                    invited_by INTEGER,
                    inviter_id INTEGER,
                    amount REAL DEFAULT 0.0,
                    is_admin INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    level TEXT DEFAULT 'Новичок 🐣'
                )
            """)

    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'games_played' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN games_played INTEGER DEFAULT 0")

    if 'is_admin' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        cursor.execute("UPDATE users SET is_admin = 0 WHERE is_admin IS NULL")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referral_profits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inviter_id INTEGER,
            amount REAL,
            FOREIGN KEY (inviter_id) REFERENCES users(user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            game_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turnover (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            turnover_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS winnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            winning_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coefficients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            coefficient REAL,
            coeff_date DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    conn.commit()
    conn.close()

def add_user_if_not_exists(user_id: int, user_name: str = None, is_admin: int = 0, conn: sqlite3.Connection = None):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        close_conn = True
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO users (user_id, user_name, balance, total_turnover, deposits, withdrawals, is_admin, games_played, level) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, user_name or "Аноним", 0.0, 0.0, 0, 0, is_admin, 0, "Новичок 🐣")
            )
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in add_user_if_not_exists: {e}")
    finally:
        if close_conn:
            conn.close()

def get_user_data(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        init_db()
        cursor.execute(
            "SELECT user_id, user_name, balance, total_turnover, deposits, withdrawals, is_admin, games_played, level "
            "FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = cursor.fetchone()
        if result:
            return {
                "user_id": result[0],
                "user_name": result[1],
                "balance": result[2],
                "total_turnover": result[3],
                "deposits": result[4],
                "withdrawals": result[5],
                "is_admin": result[6],
                "games_played": result[7] or 0,
                "level": result[8]
            }
        add_user_if_not_exists(user_id)
        return {
            "user_id": user_id,
            "user_name": "Аноним",
            "balance": 0.0,
            "total_turnover": 0.0,
            "deposits": 0,
            "withdrawals": 0,
            "is_admin": 0,
            "games_played": 0,
            "level": "Новичок 🐣"
        }
    except sqlite3.Error as e:
        logging.error(f"DB error in get_user_data: {e}")
        return {
            "user_id": user_id,
            "user_name": "Аноним",
            "balance": 0.0,
            "total_turnover": 0.0,
            "deposits": 0,
            "withdrawals": 0,
            "is_admin": 0,
            "games_played": 0,
            "level": "Новичок 🐣"
        }
    finally:
        conn.close()

def calculate_user_level(balance: float) -> str:
    current_level = LEVELS[0][1]
    for threshold, level_name in LEVELS:
        if balance >= threshold:
            current_level = level_name
        else:
            break
    return current_level

def update_user_balance(user_id: int, new_balance: float):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        init_db()
        new_level = calculate_user_level(new_balance)
        cursor.execute(
            "UPDATE users SET balance = ?, level = ? WHERE user_id = ?",
            (new_balance, new_level, user_id)
        )
        if cursor.rowcount == 0:
            add_user_if_not_exists(user_id)
            cursor.execute(
                "UPDATE users SET balance = ?, level = ? WHERE user_id = ?",
                (new_balance, new_level, user_id)
            )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in update_user_balance: {e}")
    finally:
        conn.close()

def get_user_level(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT level FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else "Новичок 🐣"
    except sqlite3.Error as e:
        logging.error(f"DB error in get_user_level: {e}")
        return "Новичок 🐣"
    finally:
        conn.close()

def get_user_level_by_games(games_played: int) -> str:
    current_level = "Новичок 🐣"
    for min_games, level_name in LEVELS:
        if games_played >= min_games:
            current_level = level_name
        else:
            break
    return current_level

def increment_games_played(user_id: int, conn: sqlite3.Connection = None):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        close_conn = True
    cursor = conn.cursor()
    max_retries = 5
    retry_delay = 0.1
    for attempt in range(max_retries):
        try:
            cursor.execute("UPDATE users SET games_played = COALESCE(games_played, 0) + 1 WHERE user_id = ?", (user_id,))
            if cursor.rowcount == 0:
                add_user_if_not_exists(user_id, conn=conn)
                cursor.execute("UPDATE users SET games_played = 1 WHERE user_id = ?", (user_id,))
            conn.commit()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            logging.error(f"DB error in increment_games_played: {e}")
            raise
        except sqlite3.Error as e:
            logging.error(f"DB error in increment_games_played: {e}")
            raise
        finally:
            if close_conn:
                conn.close()

def add_game_played(user_id: int):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO games (user_id, game_date) VALUES (?, ?)",
            (user_id, datetime.now())
        )
        increment_games_played(user_id, conn)
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in add_game_played: {e}")
    finally:
        conn.close()

def add_turnover(user_id: int, amount: float):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        init_db()
        cursor.execute(
            "INSERT INTO turnover (user_id, amount, turnover_date) VALUES (?, ?, ?)",
            (user_id, amount, datetime.now())
        )
        cursor.execute(
            "UPDATE users SET total_turnover = COALESCE(total_turnover, 0) + ? WHERE user_id = ?",
            (amount, user_id)
        )
        if cursor.rowcount == 0:
            add_user_if_not_exists(user_id)
            cursor.execute(
                "UPDATE users SET total_turnover = ? WHERE user_id = ?",
                (amount, user_id)
            )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in add_turnover: {e}")
    finally:
        conn.close()

def add_winning(user_id: int, amount: float):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        init_db()
        cursor.execute(
            "INSERT INTO winnings (user_id, amount, winning_date) VALUES (?, ?, ?)",
            (user_id, amount, datetime.now())
        )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in add_winning: {e}")
    finally:
        conn.close()

def add_coefficient(user_id: int, coefficient: float):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        init_db()
        cursor.execute(
            "INSERT INTO coefficients (user_id, coefficient, coeff_date) VALUES (?, ?, ?)",
            (user_id, coefficient, datetime.now())
        )
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"DB error in add_coefficient: {e}")
    finally:
        conn.close()

def set_inviter(ref_id: int, inviter_id: int):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET invited_by = ? WHERE user_id = ?", (inviter_id, ref_id))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error in set_inviter: {e}")
    finally:
        conn.close()

def count_ref(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE invited_by = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        logging.error(f"Database error in count_ref: {e}")
        return 0
    finally:
        conn.close()

def refka_cheks_money(user_id: int) -> float:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SUM(amount) FROM referral_profits WHERE inviter_id = ?", (user_id,))
        result = cursor.fetchone()
        return round(result[0], 2) if result[0] is not None else 0.0
    except sqlite3.Error as e:
        logging.error(f"Database error in refka_cheks_money: {e}")
        return 0.0
    finally:
        conn.close()

def add_referral_profit(inviter_id: int, amount: float):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO referral_profits (inviter_id, amount) VALUES (?, ?)", (inviter_id, amount))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error in add_referral_profit: {e}")
    finally:
        conn.close()

def get_top_10_games(time_period="all_time"):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    query = """
        SELECT u.user_name, COUNT(g.id) as game_count
        FROM users u
        JOIN games g ON u.user_id = g.user_id
    """
    params = []
    if time_period == "today":
        query += " WHERE g.game_date >= ?"
        params.append(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    elif time_period == "week":
        query += " WHERE g.game_date >= ?"
        params.append(datetime.now() - timedelta(days=7))
    elif time_period == "month":
        query += " WHERE g.game_date >= ?"
        params.append(datetime.now() - timedelta(days=30))
    query += " GROUP BY u.user_id, u.user_name ORDER BY game_count DESC LIMIT 10"
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return [(username or "Аноним", game_count) for username, game_count in result]
    except sqlite3.Error as e:
        logging.error(f"Database error in get_top_10_games: {e}")
        return []
    finally:
        conn.close()

def get_top_10_games_by_users(time_period: str = "all_time"):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        query = """
            SELECT user_name, games_played
            FROM users
            WHERE games_played > 0
        """
        params = []
        if time_period != "all_time":
            query += " AND EXISTS (SELECT 1 FROM games g WHERE g.user_id = users.user_id AND g.game_date >= ?)"
            if time_period == "today":
                params.append(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
            elif time_period == "week":
                params.append(datetime.now() - timedelta(days=7))
            elif time_period == "month":
                params.append(datetime.now() - timedelta(days=30))
        query += " ORDER BY games_played DESC LIMIT 10"
        cursor.execute(query, params)
        result = cursor.fetchall()
        return [(username or "Аноним", games_played) for username, games_played in result]
    except sqlite3.Error as e:
        logging.error(f"Database error in get_top_10_games_by_users: {e}")
        return []
    finally:
        conn.close()

def get_top_10_turnover(time_period="all_time"):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    query = """
        SELECT u.user_name, SUM(t.amount) as total_turnover
        FROM users u
        JOIN turnover t ON u.user_id = t.user_id
    """
    params = []
    if time_period == "today":
        query += " WHERE t.turnover_date >= ?"
        params.append(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    elif time_period == "week":
        query += " WHERE t.turnover_date >= ?"
        params.append(datetime.now() - timedelta(days=7))
    elif time_period == "month":
        query += " WHERE t.turnover_date >= ?"
        params.append(datetime.now() - timedelta(days=30))
    query += " GROUP BY u.user_id, u.user_name ORDER BY total_turnover DESC LIMIT 10"
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return [(username or "Аноним", total_turnover) for username, total_turnover in result]
    except sqlite3.Error as e:
        logging.error(f"Database error in get_top_10_turnover: {e}")
        return []
    finally:
        conn.close()

def get_top_10_winnings(time_period="all_time"):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    query = """
        SELECT u.user_name, SUM(w.amount) as total_winnings
        FROM users u
        JOIN winnings w ON u.user_id = w.user_id
    """
    params = []
    if time_period == "today":
        query += " WHERE w.winning_date >= ?"
        params.append(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    elif time_period == "week":
        query += " WHERE w.winning_date >= ?"
        params.append(datetime.now() - timedelta(days=7))
    elif time_period == "month":
        query += " WHERE w.winning_date >= ?"
        params.append(datetime.now() - timedelta(days=30))
    query += " GROUP BY u.user_id, u.user_name ORDER BY total_winnings DESC LIMIT 10"
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return [(username or "Аноним", total_winnings) for username, total_winnings in result]
    except sqlite3.Error as e:
        logging.error(f"Database error in get_top_10_winnings: {e}")
        return []
    finally:
        conn.close()

def get_top_10_coefficient(time_period="all_time"):
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    query = """
        SELECT u.user_name, MAX(c.coefficient) as max_coefficient
        FROM users u
        JOIN coefficients c ON u.user_id = c.user_id
    """
    params = []
    if time_period == "today":
        query += " WHERE c.coeff_date >= ?"
        params.append(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
    elif time_period == "week":
        query += " WHERE c.coeff_date >= ?"
        params.append(datetime.now() - timedelta(days=7))
    elif time_period == "month":
        query += " WHERE c.coeff_date >= ?"
        params.append(datetime.now() - timedelta(days=30))
    query += " GROUP BY u.user_id, u.user_name ORDER BY max_coefficient DESC LIMIT 10"
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return [(username or "Аноним", max_coefficient) for username, max_coefficient in result]
    except sqlite3.Error as e:
        logging.error(f"Database error in get_top_10_coefficient: {e}")
        return []
    finally:
        conn.close()

def is_user_registered(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone() is not None
        return exists
    except sqlite3.Error as e:
        logging.error(f"Database error in is_user_registered: {e}")
        return False
    finally:
        conn.close()

def is_admin(user_id: int) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] == 1 if result else False
    except sqlite3.Error as e:
        logging.error(f"Database error in is_admin: {e}")
        return False
    finally:
        conn.close()

def set_admin(user_id: int, is_admin: int) -> bool:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (user_id, user_name, is_admin, deposits, balance) VALUES (?, ?, ?, 0, 0)",
                (user_id, "Unknown", is_admin)
            )
        else:
            cursor.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (is_admin, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        logging.error(f"Database error in set_admin: {e}")
        return False
    finally:
        conn.close()