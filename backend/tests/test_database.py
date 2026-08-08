from app.core.config import TEST_DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)