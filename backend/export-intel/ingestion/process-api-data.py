import os
import pandas as pd
from pandas.errors import EmptyDataError

RAW_FOLDER = "./apidata"
OUTPUT_FILE = "clean_trade_data.csv"

print("Processing all API files...")

all_files = [
    os.path.join(RAW_FOLDER, f)
    for f in os.listdir(RAW_FOLDER)
    if f.endswith(".csv")
]

print("Total files found:", len(all_files))

processed_chunks = []

for idx, file in enumerate(all_files):
    print(f"Processing file {idx+1}/{len(all_files)}: {os.path.basename(file)}")

    try:
        df = pd.read_csv(file, low_memory=False)
    except EmptyDataError:
        print(f"⚠ Skipping empty file: {os.path.basename(file)}")
        continue

    if df.empty:
        print(f"⚠ File has no rows: {os.path.basename(file)}")
        continue

    # Ensure required columns exist
    required_columns = [
        "flowCode", "partnerCode", "aggrLevel", "isLeaf",
        "reporterDesc", "cmdCode", "period", "primaryValue"
    ]

    if not all(col in df.columns for col in required_columns):
        print(f"⚠ Missing columns in {os.path.basename(file)} — skipping")
        continue

    # Filter
    df = df[
        (df["flowCode"] == "M") &
        (df["partnerCode"] == 0) &
        (df["aggrLevel"] == 6) &
        (df["isLeaf"] == True)
    ]

    if df.empty:
        continue

    # Reduce columns
    df = df[[
        "reporterDesc",
        "cmdCode",
        "period",
        "primaryValue"
    ]]

    df = df.rename(columns={
        "reporterDesc": "country",
        "cmdCode": "hs_code",
        "period": "year",
        "primaryValue": "import_value_usd"
    })

    df["import_value_usd"] = pd.to_numeric(df["import_value_usd"], errors="coerce")
    df = df.dropna(subset=["import_value_usd"])

    if not df.empty:
        processed_chunks.append(df)

# Combine all filtered chunks
if processed_chunks:
    df = pd.concat(processed_chunks, ignore_index=True)
else:
    print("❌ No valid data found.")
    exit()

print("\nTotal rows after combining:", len(df))

# ======================================
# Extract Global Top 150 HS Codes
# ======================================

print("Computing global top 150 HS codes...")

top_codes = (
    df.groupby("hs_code")["import_value_usd"]
    .sum()
    .sort_values(ascending=False)
    .head(150)
    .index
)

df = df[df["hs_code"].isin(top_codes)]

print("Rows after limiting to top 150 HS:", len(df))
print("Unique HS codes:", df["hs_code"].nunique())
print("Unique countries:", df["country"].nunique())
print("Unique years:", df["year"].nunique())

df.to_csv(OUTPUT_FILE, index=False)

print("\nSaved cleaned dataset to:", OUTPUT_FILE)