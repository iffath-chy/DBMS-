import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
 

DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'news_db'
}

def get_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host = DB_CONFIG['host'],
            port = DB_CONFIG['port'],
            user = DB_CONFIG['user'],
            password = DB_CONFIG['password'],
            database = DB_CONFIG['database']
        )
        yield connection
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_users():
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, email, age, contact_number, bio, created_at FROM Users ORDER BY username")
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
def get_user(user_id):
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, email, age, contact_number, bio, created_at FROM Users WHERE user_id=%s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    
def create_user(username, email, age=None, contact=None, bio=None):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Users(username, email, age, contact_number, bio) VALUES (%s, %s, %s, %s, %s)", (username, email, age, contact, bio))
        connection.commit()
        cursor.close()

def update_user(user_id, username, email, age=None, contact=None, bio=None):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE Users SET username=%s, email=%s, age=%s, contact_number=%s, bio=%s WHERE user_id=%s", username, email, age, contact, bio, user_id)
        connection.commit()
        cursor.close()

def delete_user(user_id):
    with get_connection as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM Users WHERE user_id=%s", (user_id,))
        connection.commit()
        cursor.close()

def get_news():
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT news_id, title, body, created_at, user_id, username FROM News ORDER BY created_at DESC")
        rows = cursor.fetchall()
        cursor.close()
        return rows

def get_news_by_user(user_id):
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT news_id, title, body, created_at, user_id, username FROM News WHERE user_id=%s, ORDER BY created_at DESC", (user_id))
        rows = cursor.fetchall()
        cursor.close()
        return rows
    
def get_single_news(news_id):
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT news_id, title, body, created_at, user_id, username FROM News WHERE news_id=%s", (news_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
    
def create_news(title, body, user_id, username):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO News(title, body, user_id, username) VALUES (%s, %s, %s, %s)", (title, body, user_id, username))
        connection.commit()
        cursor.close()

def update_news(news_id, title, body):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE News SET title=%s, body=%s WHERE news_id=%s", (title, body, news_id))
        connection.commit()
        cursor.close()

def delete_news(news_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM News WHERE news_id=%s", (news_id,))
        connection.commit()
        cursor.close()

def search_all(q):
    qlike = f"%{q}%"
    with get_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, email, age, contact_number, bio, created_at FROM Users WHERE username LIKE %s OR email LIKE %s", (qlike, qlike))
        Users = cursor.fetchall()
        cursor.execute("SELECT news_id, title, body, created_at, user_id, username FROM News WHERE title LIKE %s OR body LIKE %s ORDER BY created_at DESC", (qlike, qlike))
        News = cursor.fetchall()
        cursor.close()
        return Users, News