from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from app.models.models import User
from app.database import SessionLocal

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword", "is_superuser": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user(client):
    """
    Тест регистрации пользователя с уже существующим email.
    Проверяет, что система корректно обрабатывает попытку регистрации дубликата.
    
    Args:
        client: Тестовый клиент FastAPI
    """
    # Первая регистрация
    response1 = client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "password": "testpassword",
            "is_superuser": True
        }
    )
    assert response1.status_code == 200
    
    # Попытка дубликата
    response2 = client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "password": "testpassword",
            "is_superuser": True
        }
    )
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]

def test_login_success(client):
    """
    Тест успешного входа в систему.
    Проверяет, что система корректно аутентифицирует пользователя и возвращает токен.
    
    Args:
        client: Тестовый клиент FastAPI
    """
    # Регистрация тестового пользователя
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword", "is_superuser": True}
    )
    
    # Попытка входа
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    
    # Проверка успешного входа
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client):
    """
    Тест входа с неверным паролем.
    Проверяет, что система корректно обрабатывает попытку входа с неверными учетными данными.
    
    Args:
        client: Тестовый клиент FastAPI
    """
    # Регистрация тестового пользователя
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpassword", "is_superuser": True}
    )
    
    # Попытка входа с неверным паролем
    response = client.post(
        "/auth/login",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    
    # Проверка ошибки аутентификации
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "nonexistent@example.com", "password": "testpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"] 