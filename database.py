# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy.ext.declarative import declarative_base

# # from config import app_settings

# SQLALCHEMY_DATABASE_URL = f"postgresql://postgres:boywithuke@localhost:5432/NTIEM_BOT"
# # don't do this put variables in .env or config.ini

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
import asyncio
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:boywithuke@localhost:5432/NTIEM_BOT"

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL)

# Declarative base for defining models
Base = declarative_base()

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
