import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text
from datetime import datetime

# --- Database Configuration ---
import streamlit as st
DB_URL = st.secrets["database"]["url"]
engine = create_engine(DB_URL)

# --- App Title ---
st.set_page_config(page_title="Packing Assistant", layout="wide")
st.title("📦 Order Packing & Docket Scan Assistant")

# --- Box Session State ---
if "current_box" not in st.session_state:
    st.session_state.current_box = ""
if "scanned_orders" not in st.session_state:
    st.session_state.scanned_orders = []

# --- Step 1: Select or Create Box ---
st.subheader("Step 1: Select or Create a Box")
with engine.connect() as conn:
    box_ids = pd.read_sql("SELECT DISTINCT box_id FROM packing_log ORDER BY box_id DESC", conn)["box_id"].tolist()

new_box = st.text_input("Create or Enter Box ID (e.g. Ben_2007_1323 or Bulk_2007_1323_1345):", value=st.session_state.current_box)
if st.button("📦 Use this Box"):
    if new_box:
        st.session_state.current_box = new_box
        st.session_state.scanned_orders = []
        st.success(f"Now working on box: {new_box}")

# --- Step 2: Scan Order ID ---
st.subheader("Step 2: Scan Order ID")
order_id = st.text_input("Scan Order Barcode (e.g. GKB201457):")

if st.button("✅ Add to Box"):
    if not st.session_state.current_box:
        st.error("Please select or create a box first.")
    else:
        # Validate order ID
        with engine.connect() as conn:
            result = conn.execute(text("SELECT store_code FROM lab_dispatch WHERE order_id = :oid"), {"oid": order_id}).fetchone()
            if result:
                # Check if already scanned
                if order_id in [o["order_id"] for o in st.session_state.scanned_orders]:
                    st.warning("Order already scanned in this session.")
                else:
                    st.session_state.scanned_orders.append({"order_id": order_id, "store_code": result[0]})
                    st.success(f"Added order {order_id} to box {st.session_state.current_box}")
            else:
                st.error("Invalid Order ID: Not found in lab_dispatch table.")

# --- Step 3: Show Scanned Orders ---
st.subheader("Scanned Orders in This Box")
if st.session_state.scanned_orders:
    df_orders = pd.DataFrame(st.session_state.scanned_orders)
    st.dataframe(df_orders)
    delete_order = st.text_input("Remove a wrongly scanned order (enter Order ID):")
    if st.button("❌ Remove Order"):
        st.session_state.scanned_orders = [o for o in st.session_state.scanned_orders if o["order_id"] != delete_order]
        st.success(f"Removed {delete_order} from current box.")

# --- Step 4: Scan Docket Number ---
st.subheader("Step 4: Scan Courier Docket Number")
docket = st.text_input("Scan Docket Number (AWB):")
courier = st.selectbox("Courier Service", ["Bluedart", "DTDC", "Verma", "Anjani", "SJ Logistics"])

if st.button("📤 Finalize & Save Box"):
    if not (st.session_state.current_box and docket and st.session_state.scanned_orders):
        st.error("Missing box, docket or orders.")
    else:
        with engine.begin() as conn:
            for o in st.session_state.scanned_orders:
                is_valid = "true"  # Can later validate store_code mapping to box
                conn.execute(text("""
                    INSERT INTO packing_log (box_id, order_id, courier, docket_no, scanned_at, is_validated)
                    VALUES (:box_id, :order_id, :courier, :docket, now(), :valid)
                """), {
                    "box_id": st.session_state.current_box,
                    "order_id": o["order_id"],
                    "courier": courier,
                    "docket": docket,
                    "valid": is_valid
                })
        st.success(f"Box {st.session_state.current_box} saved with {len(st.session_state.scanned_orders)} orders and docket {docket}.")
        st.session_state.scanned_orders = []
        st.session_state.current_box = ""
