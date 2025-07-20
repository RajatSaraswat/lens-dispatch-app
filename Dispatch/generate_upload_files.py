import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

# Database URL
DB_URL = "postgresql://postgres:Raya#281204@db.njxvvkfswpocsnwgabrn.supabase.co:5432/postgres"
engine = create_engine(DB_URL)

# Load tables
lab_df = pd.read_sql("SELECT * FROM lab_dispatch", engine)
addr_df = pd.read_sql("SELECT * FROM store_address", engine)

# Merge data
merged = lab_df.merge(addr_df, on="store_code", how="inner")

# Today's date
today_str = datetime.today().strftime("%d%m")
pickup_date = datetime.today().strftime("%d-%m-%Y")

# Separate couriers
bluedart_df = merged[merged["delivery_by"].str.lower() == "bluedart"]
dtdc_df = merged[merged["delivery_by"].str.lower() == "dtdc"]

# === Bluedart File ===
bd_records = []
for addr, group in bluedart_df.groupby("store_address"):
    store_codes = sorted(group["store_code"].unique())
    ref = f"Ben_{today_str}_{store_codes[0]}" if len(store_codes) == 1 else f"Bulk_{today_str}_{'_'.join(store_codes)}"
    mobile = group["mobile"].iloc[0] or "9548993667"
    pincode = group["pincode"].iloc[0]

    row = {
        "Reference No": ref,
        "Billing Area": "NDA",
        "Billing Customer Code": "991712",
        "Pickup Date": pickup_date,
        "Pickup Time": "1930",
        "Shipper Name": "GKB EYECARE",
        "Pickup address": "B 48 GKB EYECARE",
        "Pickup pincode": "201305",
        "Company Name": "BEN FRANKLIN OPTICIAN",
        "Delivery address": addr,
        "Delivery Pincode": pincode,
        "Product Code": "D",
        "Product Type": "NDOX",
        "Pack Type": "",
        "Piece Count": 1,
        "Actual Weight": 0.5,
        "Declared Value": 500,
        "Register Pickup": "TRUE",
        "Length": "", "Breadth": "", "Height": "",
        "To Pay Customer": "", "Sender": "GKB EYECARE", "Sender mobile": "",
        "Receiver Telephone": "", "Receiver mobile": mobile,
        "Receiver Name": "Ben Franklin / EyeGear",
        "Special Instruction": "", "Commodity Detail 1": "", "Commodity Detail 2": "", "Commodity Detail 3": "",
        "Reference No 2": "", "Reference No 3": "", "OTP Based Delivery": "",
        "Office Closure time": "1930", "AWB No": "", "Status": "", "Message": "",
        "Cluster Code": "", "Destination Area": "", "Destination Location": "",
        "Pick Up Token No": "", "Response pick up date": "",
        "Transaction Amount": "", "Wallet Balance": "", "Available Booking Amount": ""
    }
    bd_records.append(row)

# === DTDC File ===
dtdc_records = []
for addr, group in dtdc_df.groupby("store_address"):
    store_codes = sorted(group["store_code"].unique())
    ref = f"Ben_{today_str}_{store_codes[0]}" if len(store_codes) == 1 else f"Bulk_{today_str}_{'_'.join(store_codes)}"
    mobile = group["mobile"].iloc[0] or "9548993667"
    pincode = group["pincode"].iloc[0]

    row = {
        "Consignment Number": "",
        "Customer Reference Number": ref,
        "Declared Price (non-document)": 499,
        "Number of Pieces (non-document)": 1,
        "Weight(KG) (non-document)": 0.5,
        "Destination Pincode": pincode,
        "Destination Name": "BEN FRANKLIN OPTICIAN",
        "Destination Phone": mobile,
        "Destination Address Line 1": addr
    }
    dtdc_records.append(row)

# Save files
pd.DataFrame(bd_records).to_excel("Bluedart_Upload.xlsx", index=False)
pd.DataFrame(dtdc_records).to_excel("DTDC_Upload.xlsx", index=False)
print("✅ Upload files created:")
print(" - Bluedart_Upload.xlsx")
print(" - DTDC_Upload.xlsx")
