import psycopg2
from psycopg2 import sql

class DatabaseConnection:
    def __init__(self, dbname='movies', user='postgres',
                 password='password', host='localhost', port=5432):
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            print("Успішне підключення до бази даних (фільми)")
        except Exception as e:
            print(f"Помилка підключення: {e}")

    def ensure_connection(self):
        """Перевіряє, чи живе з'єднання, і відновлює його при потребі"""
        try:
            if self.conn is None or self.conn.closed != 0:
                print("З'єднання втрачено. Перепідключення до бази даних...")
                self.connect()
        except Exception:
            self.connect()

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print("З'єднання з базою закрито")

    def execute_query(self, query, params=None):
        # Перед кожним запитом перевіряємо чи з'єднання активне
        self.ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            print(f"Помилка виконання запиту: {e}")
            return None