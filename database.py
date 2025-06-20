import sqlite3
import os

DB_NAME = 'listings.db'

def get_connection():
    """Возвращает соединение с базой данных."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def db_setup():
    """Создаёт таблицы, если их нет, и добавляет недостающие колонки"""
    db_path = os.path.abspath(DB_NAME)
    print(f"[INFO] Инициализация базы данных...")
    print(f"[DEBUG] Путь к базе данных: {db_path}")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Создание таблицы listings (если нет)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                price TEXT NOT NULL,
                location_date TEXT NOT NULL,
                mileage TEXT NOT NULL,
                url TEXT NOT NULL,
                notified INTEGER DEFAULT 0
            )
        ''')

        # Проверяем, есть ли колонка category
        cursor.execute("PRAGMA table_info(listings)")
        existing_columns = [col[1] for col in cursor.fetchall()]

        # Добавляем недостающие колонки
        if "category" not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN category TEXT")
            print("[INFO] Добавлена колонка: category")

        if "category_score" not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN category_score REAL")
            print("[INFO] Добавлена колонка: category_score")

        if "delivery" not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN delivery TEXT")
            print("[INFO] Добавлена колонка: delivery")

        if "delivery_cost" not in existing_columns:
            cursor.execute("ALTER TABLE listings ADD COLUMN delivery_cost REAL")
            print("[INFO] Добавлена колонка: delivery_cost")

        conn.commit()
        print("[INFO] База данных обновлена!")

# Вызываем обновление базы при запуске
def insert_listing(listing):
    """Добавляет объявление в БД, включая доставку"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO listings 
                (id, title, price, location_date, mileage, url, category, category_score, delivery_cost, notified) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                listing['id'],
                listing['title'],
                listing['price'],
                listing['location_date'],
                listing['mileage'],
                listing['url'],
                listing.get('category', 'Неизвестно'),
                listing.get('category_score', 0.0),
                listing.get('delivery_cost', 0.0)  # Запись стоимости доставки
            ))
            conn.commit()
            print(f"[INFO] Добавлено в listings: {listing['title']} (id={listing['id']})")
            return True
    except sqlite3.IntegrityError:
        print(f"[DEBUG] Уже существует (id={listing['id']}): {listing['title']}")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка при вставке объявления: {e}")
        return False


def add_subscriber(chat_id):
    """Добавляет подписчика в базу данных, если его ещё нет"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO subscribers (chat_id) VALUES (?)', (chat_id,))
            conn.commit()
            print(f"[INFO] Подписчик {chat_id} добавлен.")
    except Exception as e:
        print(f"[ERROR] Ошибка при добавлении подписчика {chat_id}: {e}")
def get_subscribers():
    """Возвращает список всех подписчиков"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT chat_id FROM subscribers')
            subscribers = [row[0] for row in cursor.fetchall()]
            print(f"[INFO] Найдено подписчиков: {len(subscribers)}")
            return subscribers
    except Exception as e:
        print(f"[ERROR] Ошибка при получении подписчиков: {e}")
        return []
def get_new_listings():
    """Извлекает все неотправленные объявления"""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, url FROM listings WHERE notified = 0')
            listings = cursor.fetchall()

            if listings:
                print(f"[INFO] Найдено новых объявлений: {len(listings)}")
                cursor.execute('UPDATE listings SET notified = 1 WHERE notified = 0')
                conn.commit()
            else:
                print("[INFO] Новых объявлений нет.")

            return listings
    except Exception as e:
        print(f"[ERROR] Ошибка при получении новых объявлений: {e}")
        return []


db_setup()
