from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'postgresql://postgres.zxkyxiqhecetlxesweje:Jhaidiaskdfjhas@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres'

# Ensure compatibility with both psycopg (v3) and psycopg2
db_url = SQLALCHEMY_DATABASE_URL
try:
    import psycopg  # noqa: F401
except ImportError:
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(db_url)

sessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base = declarative_base()
