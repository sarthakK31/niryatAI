from db import get_connection

FILE_PATH = "./ingestion/clean_trade_data.csv"

def insert_data():
    conn = get_connection()
    cur = conn.cursor()

    with open(FILE_PATH, "r", encoding="utf-8") as f:
        next(f)  # Skip header
        cur.copy_expert("""
            COPY trade_raw(country, hs_code, year, import_value_usd)
            FROM STDIN WITH CSV
        """, f)

    conn.commit()
    conn.close()

    print("Data inserted successfully.")

if __name__ == "__main__":
    insert_data()