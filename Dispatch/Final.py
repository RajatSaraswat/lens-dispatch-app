import pandas as pd
from datetime import datetime

# === File paths ===
orders_file = "GKB Dispatch Details 19.07.2025(third route).xls.xlsx"
address_file = "EYE GEAR ADDRESS.xlsx"

# === Load files ===
orders_df = pd.read_excel(orders_file)
address_df = pd.read_excel(address_file)

# Normalize column names
orders_df.columns = orders_df.columns.str.strip()
address_df.columns = address_df.columns.str.strip()

# Rename and clean
address_df = address_df.rename(columns={"BranchID": "Store_Code", "BranchAddress": "Store_Address"})
address_df["Store_Code"] = address_df["Store_Code"].astype(str).str.strip()

# Extract store code from Customer Reference
def extract_store_code(ref):
    if isinstance(ref, str) and "/" in ref:
        return ref.split("/")[0].strip()
    return None

orders_df["Store_Code"] = orders_df["Customer Reference"].apply(extract_store_code)
orders_df["Store_Code"] = orders_df["Store_Code"].astype(str).str.strip()

# Merge orders with address info
merged_df = pd.merge(orders_df, address_df, on="Store_Code", how="inner")

# Today's date for references
today_ddmm = datetime.today().strftime("%d%m")
pickup_date = datetime.today().strftime("%d-%m-%Y")

# === Split by Courier ===
bluedart_df = merged_df[merged_df["Delivery By"].str.lower() == "bluedart"]
dtdc_df = merged_df[merged_df["Delivery By"].str.lower() == "dtdc"]

# === Bluedeart Logic ===
bd_records = []
for address, group in bluedart_df.groupby("Store_Address"):
    store_codes = sorted(group["Store_Code"].unique())
    store_str = "_".join(store_codes)
    mobile = group["Mobile"].iloc[0] if pd.notnull(group["Mobile"].iloc[0]) else "9548993667"
    pincode = group["Pincode"].iloc[0]
    ref = f"Ben_{today_ddmm}_{store_codes[0]}" if len(store_codes) == 1 else f"Bulk_{today_ddmm}_{store_str}"

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
        "Delivery address": address,
        "Delivery Pincode": pincode,
        "Product Code": "D",
        "Product Type": "NDOX",
        "Pack Type": "",
        "Piece Count": 1,
        "Actual Weight": 0.5,
        "Declared Value": 500,
        "Register Pickup": "TRUE",
        "Length": "", "Breadth": "", "Height": "",
        "To Pay Customer": "",
        "Sender": "GKB EYECARE",
        "Sender mobile": "",
        "Receiver Telephone": "",
        "Receiver mobile": mobile,
        "Receiver Name": "Ben Franklin / EyeGear",
        "Special Instruction": "",
        "Commodity Detail 1": "", "Commodity Detail 2": "", "Commodity Detail 3": "",
        "Reference No 2": "", "Reference No 3": "",
        "OTP Based Delivery": "",
        "Office Closure time": "1930",
        "AWB No": "", "Status": "", "Message": "",
        "Cluster Code": "", "Destination Area": "", "Destination Location": "",
        "Pick Up Token No": "", "Response pick up date": "",
        "Transaction Amount": "", "Wallet Balance": "", "Available Booking Amount": ""
    }
    bd_records.append(row)

# === DTDC Logic ===
dtdc_records = []
for address, group in dtdc_df.groupby("Store_Address"):
    store_codes = sorted(group["Store_Code"].unique())
    store_str = "_".join(store_codes)
    mobile = group["Mobile"].iloc[0] if pd.notnull(group["Mobile"].iloc[0]) else "9548993667"
    pincode = group["Pincode"].iloc[0]
    ref = f"Ben_{today_ddmm}_{store_codes[0]}" if len(store_codes) == 1 else f"Bulk_{today_ddmm}_{store_str}"
    row = {
        "Consignment Number": "",
        "Customer Reference Number": ref,
        "Declared Price (non-document)": 499,
        "Number of Pieces (non-document)": 1,
        "Weight(KG) (non-document)": 0.5,
        "Destination Pincode": pincode,
        "Destination Name": "BEN FRANKLIN OPTICIAN",
        "Destination Phone": mobile,
        "Destination Address Line 1": address
    }
    dtdc_records.append(row)

# === Save both files ===
pd.DataFrame(bd_records).to_excel("Bluedart_Upload.xlsx", index=False)
pd.DataFrame(dtdc_records).to_excel("DTDC_Upload.xlsx", index=False)

print("✅ Files generated:")
print(" - Bluedart_Upload.xlsx")
print(" - DTDC_Upload.xlsx")
