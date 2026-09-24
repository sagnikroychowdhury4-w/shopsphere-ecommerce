
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reviews.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

engine = create_engine(DATABASE_URL, poolclass=NullPool, future=True)
app = FastAPI(title="Synthetic E-Commerce Reviews API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}

@app.get("/reviews")
def reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    product: str | None = None,
    rating: int | None = Query(None, ge=1, le=5),
    sentiment: str | None = None,
    q: str | None = None,
):
    offset = (page - 1) * limit
    where = []
    params = {"limit": limit, "offset": offset}
    if product:
        where.append("name = :product")
        params["product"] = product
    if rating:
        where.append("reviews_rating = :rating")
        params["rating"] = rating
    if sentiment:
        where.append("sentiment = :sentiment")
        params["sentiment"] = sentiment
    if q:
        where.append("(reviews_title ILIKE :q OR reviews_text ILIKE :q)")
        params["q"] = f"%{q}%"
    clause = (" WHERE " + " AND ".join(where)) if where else ""
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM reviews{clause}"), params).scalar_one()
        result = conn.execute(text(f"""
            SELECT id, name, brand, reviews_date, reviews_didpurchase,
                   reviews_dorecommend, reviews_numhelpful, reviews_rating,
                   reviews_title, reviews_text, reviews_username, sentiment, productprice
            FROM reviews {clause}
            ORDER BY reviews_date DESC, id DESC
            LIMIT :limit OFFSET :offset
        """), params).mappings().all()
    return {"page": page, "limit": limit, "total": total, "pages": (total + limit - 1)//limit,
            "items": [dict(r) for r in result]}

@app.get("/reviews/{review_id}")
def review(review_id: str):
    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM reviews WHERE id=:id"), {"id": review_id}).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Review not found")
    return dict(row)

@app.get("/products")
def products(page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100), q: str | None = None):
    offset = (page - 1) * limit
    params = {"limit": limit, "offset": offset}
    clause = ""
    if q:
        clause = "WHERE name ILIKE :q OR brand ILIKE :q OR primarycategories ILIKE :q"
        params["q"] = f"%{q}%"
    with engine.connect() as conn:
        total = conn.execute(text(f"SELECT COUNT(*) FROM products {clause}"), params).scalar_one()
        result = conn.execute(text(f"""
            SELECT * FROM products {clause} ORDER BY name
            LIMIT :limit OFFSET :offset
        """), params).mappings().all()
    return {"page": page, "limit": limit, "total": total,
            "items": [dict(r) for r in result]}

@app.get("/stats")
def stats():
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT COUNT(*) AS reviews,
                   COUNT(DISTINCT name) AS products,
                   ROUND(AVG(reviews_rating), 2) AS avg_rating
            FROM reviews
        """)).mappings().one()
    return dict(row)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def home():
    return FileResponse("frontend/index.html")
