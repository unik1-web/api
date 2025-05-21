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

def create_test_book(client, token, isbn):
    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book for Borrow",
            "author": "Test Author",
            "publication_year": 2023,
            "isbn": isbn,
            "copies_available": 2
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]

def create_test_reader(client, token, email):
    response = client.post(
        "/readers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Reader",
            "email": email
        }
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]

def test_borrow_book(client):
    token = get_test_token(client)
    book_id = create_test_book(client, token, "borrow-unique-1")
    reader_id = create_test_reader(client, token, f"reader_{uuid.uuid4()}@example.com")
    
    response = client.post(
        "/borrows/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "due_date": "2024-12-31T23:59:59"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == book_id
    assert data["reader_id"] == reader_id
    assert data["returned_at"] is None

def test_borrow_unavailable_book(client):
    token = get_test_token(client)
    book_id = create_test_book(client, token, "borrow-unique-2")
    reader_id = create_test_reader(client, token, f"reader_{uuid.uuid4()}@example.com")
    # Заимствуем книгу первый раз
    client.post(
        "/borrows/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "due_date": "2024-12-31T23:59:59"
        }
    )
    # Пытаемся заимствовать ту же книгу снова
    response = client.post(
        "/borrows/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "due_date": "2024-12-31T23:59:59"
        }
    )
    assert response.status_code == 400

def test_return_book(client):
    token = get_test_token(client)
    book_id = create_test_book(client, token, "borrow-unique-3")
    reader_id = create_test_reader(client, token, f"reader_{uuid.uuid4()}@example.com")
    
    # Сначала берем книгу
    borrow_response = client.post(
        "/borrows/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "due_date": "2024-12-31T23:59:59"
        }
    )
    borrow_id = borrow_response.json()["id"]
    
    # Возвращаем книгу
    response = client.post(
        f"/borrows/return/{borrow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Book returned successfully"
    
    # Проверяем, что книга действительно возвращена
    borrows_response = client.get(
        f"/borrows/reader/{reader_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(borrows_response.json()) == 0

def test_return_already_returned_book(client):
    token = get_test_token(client)
    book_id = create_test_book(client, token, "borrow-unique-4")
    reader_id = create_test_reader(client, token, f"reader_{uuid.uuid4()}@example.com")
    # Заимствуем книгу
    borrow_response = client.post(
        "/borrows/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "book_id": book_id,
            "reader_id": reader_id,
            "due_date": "2024-12-31T23:59:59"
        }
    )
    borrow_id = borrow_response.json()["id"]
    # Возвращаем книгу первый раз
    client.post(
        f"/borrows/return/{borrow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Пытаемся вернуть книгу снова
    response = client.post(
        f"/borrows/return/{borrow_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400 