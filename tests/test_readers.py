import uuid
from fastapi.testclient import TestClient
from app.main import app

def get_test_token(client):
    # Регистрируем пользователя
    client.post(
        "/auth/register",
        json={"email": "test3@example.com", "password": "testpassword", "is_superuser": True}
    )
    # Получаем токен
    response = client.post(
        "/auth/login",
        data={"username": "test3@example.com", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_create_reader(client):
    token = get_test_token(client)
    response = client.post(
        "/readers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Reader",
            "email": f"reader_{uuid.uuid4()}@example.com"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Reader"
    assert "id" in data

def test_get_reader(client):
    token = get_test_token(client)
    # Сначала создаем читателя
    create_response = client.post(
        "/readers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Reader",
            "email": f"reader_{uuid.uuid4()}@example.com"
        }
    )
    reader_id = create_response.json()["id"]
    
    # Получаем читателя
    response = client.get(
        f"/readers/{reader_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == reader_id
    assert data["name"] == "Test Reader"

def test_get_nonexistent_reader(client):
    token = get_test_token(client)
    response = client.get(
        "/readers/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Reader not found"

def test_get_readers_list(client):
    token = get_test_token(client)
    # Создаем несколько читателей
    for i in range(3):
        client.post(
            "/readers/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": f"Test Reader {i}",
                "email": f"reader_{uuid.uuid4()}@example.com"
            }
        )
    
    # Получаем список читателей
    response = client.get(
        "/readers/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all("id" in reader for reader in data)
    assert all("name" in reader for reader in data)
    assert all("email" in reader for reader in data) 