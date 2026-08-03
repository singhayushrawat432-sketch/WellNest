import sqlite3
from datetime import datetime, timedelta
import hashlib

class Database:
    def __init__(self, db_name='wellnest.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            username TEXT,
            email TEXT,
            password_hash TEXT,
            pin_hash TEXT
        )''')
        # Add missing columns if they don't exist (for migration)
        try:
            self.conn.execute('ALTER TABLE users ADD COLUMN username TEXT')
        except sqlite3.OperationalError:
            pass  # Column already exists
        try:
            self.conn.execute('ALTER TABLE users ADD COLUMN email TEXT')
        except sqlite3.OperationalError:
            pass
        try:
            self.conn.execute('ALTER TABLE users ADD COLUMN password_hash TEXT')
        except sqlite3.OperationalError:
            pass
        self.conn.execute('''CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY,
            date TEXT UNIQUE,
            mood INTEGER,
            anxiety INTEGER,
            sleep_hours REAL,
            activities TEXT,
            notes TEXT
        )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS support_contacts (
            id INTEGER PRIMARY KEY,
            name TEXT,
            relationship TEXT,
            phone TEXT,
            email TEXT,
            notes TEXT
        )''')
        self.conn.execute('''CREATE TABLE IF NOT EXISTS support_messages (
            id INTEGER PRIMARY KEY,
            contact_name TEXT,
            message TEXT,
            timestamp TEXT
        )''')
        self.conn.commit()

    def create_user(self, username, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.conn.execute(
            'INSERT INTO users (name, pin_hash, username, email, password_hash) VALUES (?, ?, ?, ?, ?)',
            (username, password_hash, username, email, password_hash)
        )
        self.conn.commit()

    def get_user(self):
        cursor = self.conn.execute('SELECT * FROM users LIMIT 1')
        return cursor.fetchone()

    def login(self, username, email, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        cursor = self.conn.execute(
            'SELECT * FROM users WHERE (username = ? OR email = ?) AND (password_hash = ? OR pin_hash = ?)',
            (username, email, password_hash, password_hash)
        )
        return cursor.fetchone() is not None

    def update_user(self, username, email, password=None):
        if password:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.conn.execute(
                'UPDATE users SET name = ?, username = ?, email = ?, password_hash = ?, pin_hash = ? WHERE id = 1',
                (username, username, email, password_hash, password_hash)
            )
        else:
            self.conn.execute(
                'UPDATE users SET name = ?, username = ?, email = ? WHERE id = 1',
                (username, username, email)
            )
        self.conn.commit()

    def add_checkin(self, date, mood, anxiety, sleep_hours, activities, notes):
        self.conn.execute('''INSERT OR REPLACE INTO checkins 
            (date, mood, anxiety, sleep_hours, activities, notes) 
            VALUES (?, ?, ?, ?, ?, ?)''', 
            (date, mood, anxiety, sleep_hours, activities, notes))
        self.conn.commit()

    def get_checkin(self, date):
        cursor = self.conn.execute('SELECT * FROM checkins WHERE date = ?', (date,))
        return cursor.fetchone()

    def get_all_checkins(self):
        cursor = self.conn.execute('SELECT * FROM checkins ORDER BY date DESC')
        return cursor.fetchall()

    def add_support_contact(self, name, relationship, phone, email, notes):
        self.conn.execute(
            'INSERT INTO support_contacts (name, relationship, phone, email, notes) VALUES (?, ?, ?, ?, ?)',
            (name, relationship, phone, email, notes)
        )
        self.conn.commit()

    def get_support_contacts(self):
        cursor = self.conn.execute('SELECT * FROM support_contacts ORDER BY name')
        return cursor.fetchall()

    def add_support_message(self, contact_name, message, timestamp=None):
        timestamp = timestamp or datetime.now().strftime('%Y-%m-%d %H:%M')
        self.conn.execute(
            'INSERT INTO support_messages (contact_name, message, timestamp) VALUES (?, ?, ?)',
            (contact_name, message, timestamp)
        )
        self.conn.commit()

    def get_support_messages(self, limit=5):
        cursor = self.conn.execute(
            'SELECT contact_name, message, timestamp FROM support_messages ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

    def get_checkins_last_n_days(self, days):
        cursor = self.conn.execute(
            'SELECT * FROM checkins WHERE date >= ? ORDER BY date DESC',
            ((datetime.now() - timedelta(days=days - 1)).strftime('%Y-%m-%d'),)
        )
        return cursor.fetchall()

    def close(self):
        self.conn.close()