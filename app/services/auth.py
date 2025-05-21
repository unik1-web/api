from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from app.models.models import User
from app.schemas.user import UserCreate
import logging

# Настройка логирования
logger = logging.getLogger(__name__)
# Настройка контекста для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    Сервис для аутентификации и регистрации пользователей.
    Обрабатывает создание пользователей, хеширование паролей и проверку существования.
    """
    
    def register_user(self, db: Session, user_data: UserCreate):
        """
        Регистрация нового пользователя.
        
        Args:
            db: Сессия базы данных
            user_data: Данные пользователя для регистрации
            
        Returns:
            User: Созданный пользователь
            
        Raises:
            ValueError: Если email уже зарегистрирован
            Exception: При других ошибках регистрации
        """
        try:
            # Проверка существования пользователя
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            
            if existing_user:
                logger.debug(f"User with email {user_data.email} already exists")
                raise ValueError("Email already registered")

            # Хеширование пароля
            hashed_password = pwd_context.hash(user_data.password)
            
            # Создание пользователя
            user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                is_superuser=user_data.is_superuser
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.debug(f"User created successfully: id={user.id}, email={user.email}")
            return user
            
        except IntegrityError as e:
            # Обработка ошибки целостности базы данных (дубликат email)
            logger.error(f"IntegrityError during registration: {str(e)}")
            db.rollback()
            raise ValueError("Email already registered")
        except ValueError as e:
            # Пробрасываем ValueError дальше для обработки в маршрутизаторе
            logger.debug(f"Registration failed: {str(e)}")
            db.rollback()
            raise
        except Exception as e:
            # Обработка неожиданных ошибок
            logger.error(f"Unexpected error during registration: {str(e)}")
            db.rollback()
            raise Exception(f"Registration failed: {str(e)}") from e 