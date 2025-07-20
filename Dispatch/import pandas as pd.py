from sqlalchemy import create_engine, inspect

# ✅ Use the correct encoded password
db_url = "postgresql://postgres:Raya#281204@db.kpxdmupsnhrwuflbccpa.supabase.co:5432/postgres"
engine = create_engine(db_url)

# Create inspector
inspector = inspect(engine)

# List all schemas
schemas = inspector.get_schema_names()
print("📦 Schemas in DB:")
for schema in schemas:
    print(f"  - {schema}")

    # List tables in each schema
    tables = inspector.get_table_names(schema=schema)
    for table in tables:
        print(f"    📄 Table: {table}")

        # List columns for each table
        columns = inspector.get_columns(table, schema=schema)
        for col in columns:
            print(f"       🔹 {col['name']} ({col['type']})")

print("\n✅ Database inspection complete.")
