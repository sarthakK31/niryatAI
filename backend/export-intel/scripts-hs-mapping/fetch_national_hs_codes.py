import psycopg2
import requests
import time

conn = psycopg2.connect(
    host="localhost",
    database="testdb",
    user="postgres",
    password="password"
)

cur = conn.cursor()

cur.execute("SELECT hs_code FROM hs_code_reference")
codes = [row[0] for row in cur.fetchall()]

def lookup_code(prefix):
    url = f"https://api.trade.gov/hts/search?q={prefix}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data["results"]:
        return None
    return data["results"][0]["hts_number"]

for code in codes:

    us_code = lookup_code(code)

    cur.execute("""
        UPDATE hs_code_reference
        SET usa_hts_code = %s
        WHERE hs_code = %s
    """, (us_code, code))

    time.sleep(0.3)

conn.commit()
cur.close()
conn.close()

print("USA HTS codes populated")