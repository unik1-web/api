from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core import security
from app.core.config import settings
from app.core.deps import get_db
from app.schemas.token import Token
from app.schemas.user import User, UserCreate
from app.crud import crud_user
from app.services.auth import AuthService
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Создание маршрутизатора для аутентификации
router = APIRouter()

@router.post("/register", response_model=User)
def register_user(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Регистрация нового пользователя (библиотекаря).
    
    Args:
        db: Сессия базы данных
        user_in: Данные пользователя для регистрации
        
    Returns:
        User: Зарегистрированный пользователь
        
    Raises:
        HTTPException: При ошибках регистрации (400 - дубликат, 500 - серверная ошибка)
    """
    logger.debug(f"Attempting to register user with email: {user_in.email}")
    try:
        auth_service = AuthService()
        return auth_service.register_user(db, user_in)
    except ValueError as e:
        # Обработка ошибок валидации (дубликат email)
        logger.debug(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        # Обработка неожиданных ошибок
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during registration.",
        )

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 совместимый вход в систему, получение токена доступа для будущих запросов.
    
    Args:
        db: Сессия базы данных
        form_data: Данные формы входа (email и пароль)
        
    Returns:
        Token: Токен доступа и его тип
        
    Raises:
        HTTPException: При неверных учетных данных (401)
    """
    logger.debug(f"Attempting login for email: {form_data.username}")
    
    user = crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    
    if not user:
        logger.debug("Authentication failed - user not found or password incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"User authenticated successfully: {user.email}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 