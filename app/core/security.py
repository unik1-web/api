# Импорт необходимых компонентов
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Создание контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие пароля его хешу.
    
    Args:
        plain_password: Обычный пароль
        hashed_password: Хешированный пароль
        
    Returns:
        bool: True если пароли совпадают, False в противном случае
    """
    logger.debug(f"Verifying password. Plain: {plain_password}, Hashed: {hashed_password}")
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    Создает хеш пароля.
    
    Args:
        password: Пароль для хеширования
        
    Returns:
        str: Хешированный пароль
    """
    try:
        hashed = pwd_context.hash(password)
        logger.debug(f"Password hashed successfully. Original: {password}, Hashed: {hashed}")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создает JWT токен доступа.
    
    Args:
        data: Данные для включения в токен
        expires_delta: Время жизни токена
        
    Returns:
        str: JWT токен
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        logger.debug(f"Creating access token with data: {to_encode}")
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug("Access token created successfully")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}")
        raise

def verify_token(token: str) -> Optional[str]:
    """
    Проверяет JWT токен и извлекает email пользователя.
    
    Args:
        token: JWT токен для проверки
        
    Returns:
        Optional[str]: Email пользователя или None если токен недействителен
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None 