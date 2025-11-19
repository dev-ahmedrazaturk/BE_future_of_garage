import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Prefer env; fall back to local SQLite for MOT and Services
DATABASE_URL = os.getenv("MOT_SERVICES_DB_URL", "sqlite:///./mot_services.db")

# SQLite thread-safety setup for FastAPI
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine for the MOT and Services database
engine = create_engine(DATABASE_URL, echo=False, future=True, connect_args=connect_args)

# Create a session local for managing the DB session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models in the MOT and Services API
Base = declarative_base()

# Initialize the database (create tables)
def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
