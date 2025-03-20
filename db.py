import sqlite3


def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question_text TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()


def register_user(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user[0] if user else None


def add_question(user_id, question_text):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO questions (user_id, question_text) VALUES (?, ?)", (user_id, question_text))
    conn.commit()
    conn.close()


def get_random_question(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, question_text FROM questions WHERE user_id = ? ORDER BY RANDOM() LIMIT 1", (user_id,))
    question = cursor.fetchone()
    if question:
        cursor.execute("DELETE FROM questions WHERE id = ?", (question[0],))
        conn.commit()
    conn.close()
    return question[1] if question else None


def get_all_questions(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question_text FROM questions WHERE user_id = ?", (user_id,))
    questions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return questions


def delete_all_questions(user_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()