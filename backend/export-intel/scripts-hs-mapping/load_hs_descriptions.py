import pandas as pd
import psycopg2

df = pd.read_csv("data/hs_descriptions_filtered.csv", dtype=str)

df["hs_code"] = df["hs_code"].str.zfill(6)
conn = psycopg2.connect(
    host="localhost",
    database="testdb",
    user="postgres",
    password="password"
)

cur = conn.cursor()

for _, row in df.iterrows():
    cur.execute(
        """
        UPDATE hs_code_reference
        SET product_description = %s
        WHERE hs_code = %s
        """,
        (row["product_description"], row["hs_code"])
    )

conn.commit()
cur.close()
conn.close()

print("Descriptions inserted")