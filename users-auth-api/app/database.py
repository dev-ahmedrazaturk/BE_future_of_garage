import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Prefer env; fall back to local sqlite
DATABASE_URL = os.getenv("USERS_DB_URL", "sqlite:///./users.db")

# Needed for SQLite thread-safety with FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
