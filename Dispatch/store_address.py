import pandas as pd
from sqlalchemy import create_engine

# === CONFIG ===
EXCEL_FILE = "EYE GEAR ADDRESS.xlsx"
TABLE_NAME = "store_address"
DB_URL = "postgresql://postgres:Raya#281204@db.njxvvkfswpocsnwgabrn.supabase.co:5432/postgres"

# === Load Excel file ===
df = pd.read_excel(EXCEL_FILE)
df.columns = df.columns.str.strip()

# === Rename columns to match DB ===
df = df.rename(columns={
    "Store_Code": "store_code",
    "StateName": "state_name",
    "City": "city",
    "Store_Name": "store_name",
    "Store_Address": "store_address",
    "Pincode": "pincode",
    "Mobile": "mobile",
    "Delivery By": "delivery_by"
})

# === Remove rows with missing required values ===
required_columns = [
    "store_code", "state_name", "city", "store_name",
    "store_address", "pincode", "mobile", "delivery_by"
]
df = df.dropna(subset=required_columns)

# Remove extra spaces in string fields
for col in df.select_dtypes(include="object").columns:
    df[col] = df[col].astype(str).str.strip()

# === Upload to PostgreSQL ===
engine = create_engine(DB_URL)

try:
    df.to_sql(TABLE_NAME, engine, if_exists="append", index=False)
    print(f"✅ Uploaded {len(df)} rows to '{TABLE_NAME}' table.")
except Exception as e:
    print("❌ Upload failed:")
    print(e)
