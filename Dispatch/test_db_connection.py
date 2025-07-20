import pandas as pd
from sqlalchemy import create_engine

# Your database.build connection URL
db_url = "postgresql://postgres@44u5cem3hrzmfig1.browser.db.build/postgres?sslmode=require"

# Create SQLAlchemy engine
engine = create_engine(db_url)

# Read data from lab_dispatch
lab_dispatch_df = pd.read_sql("SELECT * FROM lab_dispatch LIMIT 5", engine)
print("🧪 Lab Dispatch Sample:\n", lab_dispatch_df)

# Read data from store_address
store_address_df = pd.read_sql("SELECT * FROM store_address LIMIT 5", engine)
print("🏬 Store Address Sample:\n", store_address_df)

# Save to Excel (optional)
lab_dispatch_df.to_excel("lab_dispatch_sample.xlsx", index=False)
store_address_df.to_excel("store_address_sample.xlsx", index=False)
