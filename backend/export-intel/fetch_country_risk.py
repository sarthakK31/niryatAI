import requests
import pandas as pd
from db import get_connection

# Map your dataset country names to ISO3 codes
COUNTRY_ISO = {
    "USA": "USA",
    "China": "CHN",
    "Germany": "DEU",
    "Switzerland": "CHE",
    "Belgium": "BEL",
    "France": "FRA",
    "Italy": "ITA",
    "Spain": "ESP",
    "Japan": "JPN",
    "United Kingdom": "GBR",
    "Netherlands": "NLD",
    "Indonesia": "IDN",
    "New Zealand": "NZL",
    "Sweden": "SWE",
    "Norway": "NOR",
    "Russian Federation": "RUS",
    "Qatar": "QAT",
    "Pakistan": "PAK",
    "Romania": "ROM",
    "Brazil": "BRA",
    "Austria": "AUT",
    "Australia": "AUS",
    "Ireland": "IRL",
    "Singapore": "SGP",
    "Canada": "CAN",
    "Rep. of Korea": "KOR",
    "Portugal": "PRT",
    "Finland": "FIN",
    "Colombia": "COL",
    "Saudi Arabia": "SAU",
    "Argentina": "ARG",
    "United Arab Emirates": "ARE",
    "Greece": "GRC",
    "Egypt": "EGY",
    "Chile": "CHL",
    "Türkiye": "TUR",
    "Israel": "ISR",
    "South Africa": "ZAF",
    "Mexico": "MEX",
    "Peru": "PER",
    "Malaysia": "MYS",
    "Poland": "POL",
    "Kuwait": "KWT",
    "Denmark": "DNK",
    "Philippines": "PHL",
    "Thailand": "THA",
}

INDICATOR = "PV.EST"

def normalize(series):
    return (series - series.min()) / (series.max() - series.min())

def fetch_risk_data():

    records = []

    for country, iso in COUNTRY_ISO.items():
        url = f"https://api.worldbank.org/v2/country/{iso}/indicator/{INDICATOR}?format=json"

        response = requests.get(url)
        data = response.json()

        if len(data) < 2 or not data[1]:
            continue

        # Get most recent non-null value
        for entry in data[1]:
            if entry["value"] is not None:
                stability = entry["value"]
                break
        else:
            continue

        records.append((country, stability))

    df = pd.DataFrame(records, columns=["country", "stability_index"])

    # Normalize stability to risk
    df["risk_score"] = 1 - normalize(df["stability_index"])

    return df

def insert_risk(df):

    conn = get_connection()
    cur = conn.cursor()

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO country_risk (country, stability_index, risk_score)
            VALUES (%s, %s, %s)
            ON CONFLICT (country)
            DO UPDATE SET
                stability_index = EXCLUDED.stability_index,
                risk_score = EXCLUDED.risk_score
        """, (
            row["country"],
            float(row["stability_index"]),
            float(row["risk_score"])
        ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    df = fetch_risk_data()
    insert_risk(df)
    print("Country risk data inserted successfully.")