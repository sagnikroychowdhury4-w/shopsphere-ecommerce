import os
from sqlalchemy import create_engine, inspect

database_url = os.environ["DATABASE_URL"]

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

engine = create_engine(database_url)

inspector = inspect(engine)

if "reviews" not in inspector.get_table_names():
    print("Database is empty. Starting seed...")
    os.system("python backend/seed.py")
else:
    print("Database already initialized. Skipping seed.")