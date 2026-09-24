
import csv, os, re
from sqlalchemy import create_engine, text
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reviews.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL, future=True)

csv_file = Path(os.getenv("CSV_FILE", "data/reviews_150k.csv"))

cols = [
"id","dateAdded","dateUpdated","name","brand","manufacturer","categories","primaryCategories",
"reviews.date","reviews.didPurchase","reviews.doRecommend","reviews.numHelpful","reviews.rating",
"reviews.title","reviews.text","reviews.username","sentiment","productPrice"
]
db_cols = [re.sub(r'[^a-zA-Z0-9_]', '_', c).lower() for c in cols]

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS reviews"))
    conn.execute(text("""
    CREATE TABLE reviews (
      id VARCHAR(32) PRIMARY KEY,
      dateadded DATE, dateupdated DATE, name TEXT, brand TEXT, manufacturer TEXT,
      categories TEXT, primarycategories TEXT, reviews_date DATE,
      reviews_didpurchase BOOLEAN, reviews_dorecommend BOOLEAN,
      reviews_numhelpful INTEGER, reviews_rating INTEGER,
      reviews_title TEXT, reviews_text TEXT, reviews_username TEXT,
      sentiment VARCHAR(20), productprice NUMERIC(10,2)
    )
    """))
    conn.execute(text("DROP TABLE IF EXISTS products"))
    conn.execute(text("""
    CREATE TABLE products (
      name TEXT PRIMARY KEY, brand TEXT, manufacturer TEXT, categories TEXT,
      primarycategories TEXT, productprice NUMERIC(10,2)
    )
    """))

    with csv_file.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            batch.append({db_cols[i]: row[cols[i]] for i in range(len(cols))})
            if len(batch) >= 2000:
                conn.execute(text(f"""
                    INSERT INTO reviews ({",".join(db_cols)})
                    VALUES ({",".join(":"+c for c in db_cols)})
                """), batch)
                batch.clear()
        if batch:
            conn.execute(text(f"""
                INSERT INTO reviews ({",".join(db_cols)})
                VALUES ({",".join(":"+c for c in db_cols)})
            """), batch)

    conn.execute(text("""
      INSERT INTO products(name, brand, manufacturer, categories, primarycategories, productprice)
      SELECT name, MIN(brand), MIN(manufacturer), MIN(categories), MIN(primarycategories), ROUND(AVG(productprice),2)
      FROM reviews GROUP BY name
    """))
    conn.execute(text("CREATE INDEX idx_reviews_name ON reviews(name)"))
    conn.execute(text("CREATE INDEX idx_reviews_rating ON reviews(reviews_rating)"))
    conn.execute(text("CREATE INDEX idx_reviews_sentiment ON reviews(sentiment)"))
    conn.execute(text("CREATE INDEX idx_reviews_date ON reviews(reviews_date DESC)"))
print("Seed complete.")
