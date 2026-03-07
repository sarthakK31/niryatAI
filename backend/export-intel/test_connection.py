from db import get_connection

try:
    conn = get_connection()
    print("Connected successfully to Postgres!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)