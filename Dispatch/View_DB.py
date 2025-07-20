import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# -------------------------------
# 🚀 DB CONFIG (escape '#' as %23)
# -------------------------------
import streamlit as st
DB_URL = st.secrets["database"]["url"]
engine = create_engine(DB_URL)

st.set_page_config(page_title="📊 Lens Dispatch Viewer", layout="wide")
st.title("📦 Lens Dispatch & Logistics Database Viewer")

# -------------------------------
# 📦 Table Selector with Refresh
# -------------------------------
@st.cache_data(ttl=600)
def get_tables():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        return [row[0] for row in result]

if st.button("🔄 Refresh Tables"):
    st.cache_data.clear()

tables = get_tables()
if not tables:
    st.warning("No tables found in the database.")
    st.stop()

selected_table = st.selectbox("📁 Select a table to view/edit", tables)

# -------------------------------
# 📄 Load Data from Selected Table
# -------------------------------
@st.cache_data(ttl=600)
def load_table_data(table_name):
    with engine.connect() as conn:
        query = text(f"SELECT * FROM public.{table_name}")
        return pd.read_sql(query, conn)

df = load_table_data(selected_table)

if df.empty:
    st.info(f"Table `{selected_table}` is empty.")
else:
    st.subheader(f"📋 Data from `{selected_table}`")

    # -------------------------------
    # 🔍 Search and Filter
    # -------------------------------
    search_cols = df.select_dtypes(include=[object, "string", "int", "float"]).columns.tolist()
    search_col = st.selectbox("🔍 Search in column:", search_cols)
    search_val = st.text_input("Enter value to filter by:")

    if search_val:
        filtered_df = df[df[search_col].astype(str).str.contains(search_val, case=False, na=False)]
    else:
        filtered_df = df

    st.markdown(f"**🧾 Showing {len(filtered_df)} of {len(df)} records**")
    edited_df = st.data_editor(filtered_df, use_container_width=True, num_rows="dynamic", key="editable_table")

    # -------------------------------
    # 💾 Save Changes
    # -------------------------------
    if st.button("💾 Save Changes to DB"):
        try:
            with engine.begin() as conn:
                for i, row in edited_df.iterrows():
                    set_clause = ", ".join([f"{col} = :{col}" for col in filtered_df.columns if col != filtered_df.columns[0]])
                    primary_key = filtered_df.columns[0]
                    update_query = text(f"""
                        UPDATE public.{selected_table}
                        SET {set_clause}
                        WHERE {primary_key} = :{primary_key}
                    """)
                    conn.execute(update_query, row.to_dict())
            st.success("✅ Changes saved successfully.")
            st.cache_data.clear()
        except SQLAlchemyError as e:
            st.error(f"❌ Failed to save changes: {e}")

# -------------------------------
# ➕ Add New Row
# -------------------------------
st.markdown("---")
st.subheader(f"➕ Add New Record to `{selected_table}`")

with engine.connect() as conn:
    cols = pd.read_sql(f"SELECT * FROM public.{selected_table} LIMIT 1", conn).columns

new_row = {}
for col in cols:
    new_row[col] = st.text_input(f"{col}", key=f"new_{col}")

if st.button("➕ Add Record"):
    try:
        placeholders = ", ".join([f":{col}" for col in cols])
        col_names = ", ".join(cols)
        insert_query = text(f"INSERT INTO public.{selected_table} ({col_names}) VALUES ({placeholders})")

        with engine.begin() as conn:
            conn.execute(insert_query, new_row)

        st.success("✅ New record added successfully.")
        st.cache_data.clear()
    except SQLAlchemyError as e:
        st.error(f"❌ Failed to add record: {e}")
