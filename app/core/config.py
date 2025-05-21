# Импорт необходимых компонентов
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Класс настроек приложения.
    Загружает конфигурацию из переменных окружения и .env файла.
    """
    DATABASE_URL: str  # URL для подключения к базе данных
    SECRET_KEY: str    # Секретный ключ для JWT токенов
    ALGORITHM: str     # Алгоритм шифрования для JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Время жизни токена в минутах

    class Config:
        env_file = ".env"  # Путь к файлу с переменными окружения

# Создание экземпляра настроек
settings = Settings() 