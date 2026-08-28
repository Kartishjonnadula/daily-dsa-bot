import sqlite3
from pathlib import Path

DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE = DATA_DIR / "neetcode.db"

connection=None
def get_connection():
    global connection
    if connection is None:
        connection = sqlite3.connect(DATABASE_FILE)
        connection.row_factory = sqlite3.Row
    return connection

def initialize_database():
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS registrations (user_id INTEGER NOT NULL,guild_id INTEGER NOT NULL,channel_id INTEGER NOT NULL,registered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (user_id, guild_id));
            CREATE TABLE IF NOT EXISTS rotations (id INTEGER PRIMARY KEY AUTOINCREMENT,started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,completed_at TEXT);
            CREATE TABLE IF NOT EXISTS rotation_problems (rotation_id INTEGER NOT NULL,problem_id TEXT NOT NULL,used_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,PRIMARY KEY (rotation_id, problem_id),FOREIGN KEY (rotation_id)REFERENCES rotations(id));
            CREATE TABLE IF NOT EXISTS daily_problems (problem_date TEXT PRIMARY KEY,rotation_id INTEGER NOT NULL,problem_1_id TEXT NOT NULL,problem_2_id TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (rotation_id)REFERENCES rotations(id));
            """
        )

# ---- REGISTRATIONS ----
def register_user(user_id,guild_id,channel_id):
    with get_connection() as connection: connection.execute("""INSERT INTO registrations (user_id,guild_id,channel_id) VALUES (?, ?, ?) ON CONFLICT(user_id, guild_id) DO UPDATE SET channel_id = excluded.channel_id, registered_at = CURRENT_TIMESTAMP""",(user_id,guild_id,channel_id))

def unregister_user(user_id,guild_id):
    with get_connection() as connection: return connection.execute("""DELETE FROM registrations WHERE user_id = ? AND guild_id = ?""",(user_id,guild_id)).rowcount > 0

def get_registered_users():
    with get_connection() as connection: return connection.execute("""SELECT user_id, guild_id, channel_id FROM registrations ORDER BY channel_id, registered_at""").fetchall()

# ---- ROTATIONS ----
def get_current_rotation(): 
    with get_connection() as connection: return connection.execute("""SELECT id, started_at, completed_at FROM rotations WHERE completed_at IS NULL ORDER BY id DESC LIMIT 1""").fetchone()

def create_rotation(): 
    with get_connection() as connection: return connection.execute("""INSERT INTO rotations DEFAULT VALUES""").lastrowid

def complete_rotation(rotation_id):
    with get_connection() as connection: connection.execute( """ UPDATE rotations SET completed_at = CURRENT_TIMESTAMP WHERE id = ?""",(rotation_id))

def get_used_problem_ids(rotation_id):
    with get_connection() as connection: return { row["problem_id"] for row in connection.execute("""SELECT problem_id FROM rotation_problems WHERE rotation_id = ?""", (rotation_id)).fetchall()}

def mark_problems_used( rotation_id,problems):
    with get_connection() as connection: connection.executemany("""INSERT INTO rotation_problems (rotation_id,problem_id) VALUES (?, ?)""",[(rotation_id,problem["id"]) for problem in problems])

# DAILY PROBLEMS
def get_daily_problems(problem_date):
    with get_connection() as connection: return connection.execute("""SELECT problem_date, rotation_id, problem_1_id, problem_2_id FROM daily_problems WHERE problem_date = ?""",(problem_date)).fetchone()

def save_daily_problems(problem_date,rotation_id,problem_1_id,problem_2_id):
    with get_connection() as connection: connection.execute("""INSERT OR REPLACE INTO daily_problems (problem_date,rotation_id,problem_1_id,problem_2_id) VALUES (?, ?, ?, ?) """,(problem_date,rotation_id,problem_1_id,problem_2_id))