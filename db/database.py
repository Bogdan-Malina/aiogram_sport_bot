import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)

load_dotenv()


CONNECTION = os.getenv("CONNECTION")

engine = create_async_engine(
    CONNECTION,
    echo=True,
)

session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
