from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.security import get_password_hash, verify_password
from app.models.models import User
from app.schemas.user import UserCreate, UserUpdate
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

def get_by_email(db: Session, email: str) -> Optional[User]:
    logger.debug(f"Looking up user by email: {email}")
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            logger.debug(f"User found: id={user.id}, email={user.email}, is_superuser={user.is_superuser}")
        else:
            logger.debug(f"User not found: {email}")
        return user
    except Exception as e:
        logger.error(f"Error looking up user: {str(e)}")
        return None

def authenticate(db: Session, *, email: str, password: str) -> Optional[User]:
    logger.debug(f"Attempting to authenticate user: {email}")
    try:
        user = get_by_email(db, email=email)
        if not user:
            logger.debug(f"Authentication failed: User not found: {email}")
            return None
        
        logger.debug(f"Verifying password for user: {email}")
        if not verify_password(password, user.hashed_password):
            logger.debug(f"Authentication failed: Invalid password for user: {email}")
            return None
        
        logger.debug(f"Authentication successful for user: {email}")
        return user
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return None

def create(db: Session, *, obj_in: UserCreate) -> User:
    logger.debug(f"Creating new user with email: {obj_in.email}")
    try:
        hashed_password = get_password_hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            hashed_password=hashed_password,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.debug(f"User created successfully: id={db_obj.id}, email={db_obj.email}")
        return db_obj
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError in create: {str(e)}")
        raise ValueError("Email already registered")
    except Exception as e:
        logger.error(f"Unexpected error during registration: {type(e)}: {str(e)}")
        db.rollback()
        raise ValueError("An unexpected error occurred during registration")

def update(
    db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj 