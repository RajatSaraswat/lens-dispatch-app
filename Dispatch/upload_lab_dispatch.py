import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import os

# Database connection
DB_URL = "postgresql://postgres:Raya#281204@db.njxvvkfswpocsnwgabrn.supabase.co:5432/postgres"
engine = create_engine(DB_URL)

# === Load your Excel dispatch file ===
dispatch_file = "D:\Dispatch\lab_dispatch_data.xlsx"  # <- Update this filename if needed
df = pd.read_excel(dispatch_file, usecols=["Ord. No", "Ord.Date", "Customer Reference"])

# === Rename and clean columns ===
df.columns = ["order_id", "order_date", "customer_reference"]
df = df.dropna(subset=["order_id", "customer_reference"])  # Ensure critical data is present

# === Extract store_code from Customer Reference ===
def extract_store_code(ref):
    try:
        return ref.split("/")[0].strip()
    except:
        return None

df["store_code"] = df["customer_reference"].apply(extract_store_code)

# === Fetch valid store codes from DB ===
valid_store_codes = pd.read_sql("SELECT store_code FROM store_address", engine)
valid_codes_set = set(valid_store_codes["store_code"].astype(str))

# === Separate valid and invalid entries ===
df["store_code"] = df["store_code"].astype(str)
valid_rows = df[df["store_code"].isin(valid_codes_set)]
invalid_rows = df[~df["store_code"].isin(valid_codes_set)]

# === Upload valid rows to lab_dispatch ===
if not valid_rows.empty:
    valid_rows.to_sql("lab_dispatch", engine, if_exists="append", index=False)
    print(f"✅ Uploaded {len(valid_rows)} rows to lab_dispatch.")
else:
    print("⚠️ No valid rows found to upload.")

# === Log invalid/missing store codes ===
if not invalid_rows.empty:
    log_file = "missing_store_codes.csv"
    invalid_rows[["order_id", "customer_reference", "store_code"]].to_csv(log_file, index=False)
    print(f"⚠️ Skipped {len(invalid_rows)} rows. Logged missing store codes to: {log_file}")
else:
    print("✅ No missing store codes.")

