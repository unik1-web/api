# Импорт необходимых компонентов SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Создание движка базы данных с использованием URL из настроек
engine = create_engine(settings.DATABASE_URL)

# Создание фабрики сессий с отключенным автокоммитом и автофлашем
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создание базового класса для моделей
Base = declarative_base()

def get_db():
    """
    Генератор для получения сессии базы данных.
    Гарантирует закрытие сессии после использования.
    
    Yields:
        Session: Сессия базы данных
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 