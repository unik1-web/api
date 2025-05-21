import os
import sys
import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

# Добавляем путь к корневой директории проекта в PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import Base, get_db
from app.core.config import settings

# Настройка тестовой базы данных
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:777@localhost:5433/library_test_db"

@pytest.fixture(scope="function")
def db():
    # Создаем таблицы с помощью Alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
    
    # Создаем engine и sessionmaker только после применения миграций
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Создаем все таблицы через SQLAlchemy Base
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Удаляем все таблицы с помощью Alembic
        command.downgrade(alembic_cfg, "base")
        engine.dispose()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

# Отключаем предупреждения о asyncio
pytest.register_assert_rewrite("tests.test_auth")
pytest.register_assert_rewrite("tests.test_books")
pytest.register_assert_rewrite("tests.test_borrows")

# Настройка asyncio для Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) 