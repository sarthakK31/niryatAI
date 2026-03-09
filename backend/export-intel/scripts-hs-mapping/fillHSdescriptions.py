import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="testdb",
    user="postgres",
    password="password"
)

cur = conn.cursor()

# example dictionary for now
HS_MAP = {
    "100630": "Semi-milled or wholly milled rice",
    "120510": "Low erucic acid rape or colza seeds",
    "180100": "Cocoa beans whole or broken",
}

for code, desc in HS_MAP.items():
    cur.execute(
        """
        UPDATE hs_code_reference
        SET product_description=%s
        WHERE hs_code=%s
        """,
        (desc, code)
    )

conn.commit()
cur.close()
conn.close()