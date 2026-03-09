import pandas as pd

# load HS codes from your DB export
codes = pd.read_csv("hs_codes.csv")

# load HS dataset
hs = pd.read_csv("data/harmonized-system.csv")

# normalize column names
codes["hs_code"] = codes["hs_code"].astype(str).str.zfill(6)
hs["hscode"] = hs["hscode"].astype(str).str.zfill(6)

# keep only HS6 rows
hs = hs[hs["level"] == 6]

# filter only codes present in your system
filtered = hs[hs["hscode"].isin(codes["hs_code"])]

# rename columns to match DB
filtered = filtered.rename(columns={
    "hscode": "hs_code",
    "description": "product_description"
})

# keep only needed columns
filtered = filtered[["hs_code", "product_description"]]

manual = {
    "300220": "vaccines for human medicine",
    "382200": "Diagnostic or laboratory reagents on a backing, prepared diagnostic/laboratory reagents.",
    "851712": "Telephones for cellular (mobile) networks or for other wireless networks"
}

# add the data for a few missing fields manually
for code, desc in manual.items():
    filtered.loc[len(filtered)] = [code, desc]

# export
filtered.to_csv("data/hs_descriptions_filtered.csv", index=False)

print("Generated dataset with", len(filtered), "HS codes")