import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connect = psycopg2.connect(
    host=os.getenv("DB_host"),
    user=os.getenv("DB_user"),
    password=os.getenv("DB_password"),
    port=os.getenv("DB_port"),
    dbname=os.getenv("DB_name")
)

    cursor = connect.cursor()

    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Database version: {version[0]}")

    cursor.close()
except Exception as e:
    print(f"Error connecting to database {e}")
#! finally:
#!     if 'connect' in locals() and connect:
#!         connect.close()
#!         print("Сonnection interrupted")

#? Реализация добавления записи в таблицу с нуля
def insert_in_db(name: str, type: str) -> str:
    try:
        cursor = connect.cursor()
        cursor.execute("INSERT INTO categories(name, type) VALUES(%s, %s) ON CONFLICT (name) DO NOTHING", (name, type))
        connect.commit()
    except Exception as e:
        connect.rollback()
    finally:
        cursor.close()

#? Получение id категории из таблицы
def get_category_id(name: str, type: str) -> int:
    cursor = None
    try:
        cursor = connect.cursor()
        cursor.execute("SELECT category_id FROM categories WHERE name = %s and type = %s", (name, type))
        result = cursor.fetchone()

        if result is not None:
            return result[0]
        
        cursor.execute("INSERT INTO categories(name, type) VALUES(%s, %s) RETURNING category_id;", (name, type))
        category_id = cursor.fetchone()[0]
        connect.commit()
        return category_id
    except Exception as e:
        connect.rollback()
        raise e
    finally:
        cursor.close()
    

#? Реализация добавления записи в таблицу transactions с уже выбранной категорией
def insert_in_transactions(category_id: int, amount: float):
    cursor = None
    try:
        cursor = connect.cursor()
        cursor.execute("INSERT INTO transactions(category_id, amount) VALUES (%s, %s) RETURNING *;", (category_id, amount))
        connect.commit()
        return("entry succses added")
    except Exception as e:
        return(f"finished with error {e}")
    finally:
        if cursor is not None:
            cursor.close()

#! Реализация удаления записи из transactions
def delete_from_db(id: int) -> str:
    try:
        cursor = connect.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = %s", (str(id)))
        connect.commit()
        return(f"entry with number {id} deleted")
    except Exception as e:
        return(f"finished with error {e}")
    finally:
        cursor.close()

#! Последние 5 добавленных записей
def last_five_entrys():
    try:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT 5")
        ids = cursor.fetchall()
        foam = []
        for row in ids:
            id, category_id, amount, created_at = row
            foam.append([id, category_id, int(amount), created_at.strftime("%d.%m.%y %H:%M:%S")])
        return foam
    except Exception as e:
        raise e
    finally:
        cursor.close()
        foam = []

#! Показывает количество денег на счете прямо сейчас
def money_on_account():
    cursor = None
    try:
        cursor = connect.cursor()
        cursor.execute("SELECT ((SELECT SUM(amount) AS sum FROM transactions WHERE category_id IN (SELECT category_id FROM categories WHERE type = 'Доход')) - (SELECT SUM(amount) AS sum FROM transactions WHERE category_id IN (SELECT category_id FROM categories WHERE type = 'Расход')))")
        result = cursor.fetchall()
        balance = result[0][0]
        return float(balance)
    except Exception as e:
        return f"finished with error {e}"
    finally:
        if cursor is not None:
            cursor.close()

#! Топ 5 популярных категорий
def ten_popular_categories():
    cursor = None
    try:
        cursor = connect.cursor()
        cursor.execute("SELECT category_id, name, COUNT(id) AS amount_entrys FROM categories LEFT JOIN transactions USING(category_id) GROUP BY category_id, name ORDER BY amount_entrys DESC LIMIT 5")
        result = cursor.fetchall()
        return result
    except Exception as e:
        return f"finished with error {e}"
    finally:
        if cursor is not None:
            cursor.close()
        result = 0