import pandas as pd
import numpy as np
from db import get_connection

def normalize(series):
    if series.max() == series.min():
        return pd.Series([0.5] * len(series), index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def compute_intelligence():

    conn = get_connection()

    print("Loading trade data from DB...")
    df = pd.read_sql(
        "SELECT country, hs_code, year, import_value_usd FROM trade_raw",
        conn
    )

    grouped = df.groupby(["country", "hs_code"])

    records = []

    for (country, hs), group in grouped:

        group = group.sort_values("year")

        if len(group) < 3:
            continue  # need enough data for trend

        mean_val = group["import_value_usd"].mean()
        std_val = group["import_value_usd"].std()
        total_import = group["import_value_usd"].sum()

        if mean_val == 0:
            continue

        # CAGR calculation
        first = group.iloc[0]["import_value_usd"]
        last = group.iloc[-1]["import_value_usd"]
        years = len(group) - 1

        if first == 0:
            continue

        cagr = ((last / first) ** (1 / years)) - 1

        # Cap extreme growth at 40%
        cagr = min(cagr, 0.4)

        # Coefficient of Variation (stability)
        cv = std_val / mean_val

        records.append(
            (country, hs, cagr, cv, total_import)
        )

    result_df = pd.DataFrame(
        records,
        columns=[
            "country",
            "hs_code",
            "avg_growth_5y",
            "cv",
            "total_import"
        ]
    )

    # Remove very small markets (below $50M total over 6 years)
    result_df = result_df[result_df["total_import"] > 50_000_000]

    print("Records after filtering small markets:", len(result_df))

    # Market size (log scaled)
    result_df["size_log"] = np.log(result_df["total_import"])

    # Normalize components
    result_df["size_norm"] = normalize(result_df["size_log"])
    result_df["growth_norm"] = normalize(result_df["avg_growth_5y"])
    result_df["stability_norm"] = 1 - normalize(result_df["cv"])

    risk_df = pd.read_sql("SELECT * FROM country_risk", conn)

    result_df = result_df.merge(risk_df[["country", "risk_score"]], 
                            on="country", how="left")

    result_df["risk_score"] = result_df["risk_score"].fillna(0.5)

    # Final Opportunity Score
    result_df["opportunity_score"] = (
        0.40  * result_df["size_norm"] +
        0.25  * result_df["growth_norm"] +
        0.25  * result_df["stability_norm"]+
        0.10  * result_df["risk_score"]
    )

    def generate_summary(row):
        growth_pct = round(row["avg_growth_5y"] * 100, 2)
        total_import_billions = round(row["total_import"] / 1_000_000_000, 2)

        return (
            f"{row['country']} imports HS {row['hs_code']} with "
            f"{growth_pct}% average annual growth. "
            f"Total imports over 6 years: ${total_import_billions}B. "
            f"Political risk score: {round(row['risk_score'],2)}. "
            f"Opportunity score: {round(row['opportunity_score'],2)}."
        )

    result_df["ai_summary"] = result_df.apply(generate_summary, axis=1)

    # Insert into DB
    cur = conn.cursor()

    for _, row in result_df.iterrows():
        cur.execute("""
            INSERT INTO market_intelligence
            (country, hs_code, avg_growth_5y, volatility, total_import, opportunity_score, ai_summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row["country"],
            row["hs_code"],
            float(row["avg_growth_5y"]),
            float(row["cv"]),
            float(row["total_import"]),
            float(row["opportunity_score"]),
            str(row["ai_summary"])
        ))

    conn.commit()
    conn.close()

    print("Market intelligence computed successfully.")
    print("Total intelligence rows:", len(result_df))


if __name__ == "__main__":
    compute_intelligence()