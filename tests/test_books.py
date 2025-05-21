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

def test_create_book(client):
    token = get_test_token(client)
    response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book",
            "author": "Test Author",
            "publication_year": 2023,
            "isbn": "book-unique-1",
            "copies_available": 2
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["isbn"] == "book-unique-1"
    assert data["copies_available"] == 2
    assert "id" in data

def test_get_books(client):
    token = get_test_token(client)
    response = client.get(
        "/books/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "title" in data[0]
        assert "author" in data[0]

def test_get_book(client):
    token = get_test_token(client)
    # Сначала создаем книгу
    create_response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book",
            "author": "Test Author",
            "publication_year": 2023,
            "isbn": "book-unique-2",
            "copies_available": 2
        }
    )
    book_id = create_response.json()["id"]
    
    # Получаем книгу
    response = client.get(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Test Book"
    assert data["author"] == "Test Author"
    assert data["isbn"] == "book-unique-2"
    assert data["copies_available"] == 2

def test_update_book(client):
    token = get_test_token(client)
    # Сначала создаем книгу
    book_response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "book-unique-3",
            "description": "Test Description"
        }
    )
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]

    # Обновляем книгу
    response = client.put(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Updated Book",
            "author": "Updated Author",
            "isbn": "book-unique-3",
            "description": "Updated Description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book_id
    assert data["title"] == "Updated Book"
    assert data["author"] == "Updated Author"
    assert data["description"] == "Updated Description"

def test_delete_book(client):
    token = get_test_token(client)
    # Сначала создаем книгу
    book_response = client.post(
        "/books/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Book",
            "author": "Test Author",
            "isbn": "book-unique-4",
            "description": "Test Description"
        }
    )
    assert book_response.status_code == 200
    book_id = book_response.json()["id"]

    # Удаляем книгу
    response = client.delete(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Проверяем, что книга удалена
    get_response = client.get(
        f"/books/{book_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_response.status_code == 404

def test_get_nonexistent_book(client):
    token = get_test_token(client)
    response = client.get(
        "/books/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"

def test_get_books_list(client):
    token = get_test_token(client)
    # Создаем несколько книг
    for i in range(3):
        client.post(
            "/books/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"Test Book {i}",
                "author": f"Test Author {i}",
                "publication_year": 2023,
                "isbn": f"book-list-{i}",
                "copies_available": 2
            }
        )
    
    # Получаем список книг
    response = client.get(
        "/books/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all("id" in book for book in data)
    assert all("title" in book for book in data)
    assert all("author" in book for book in data)
    assert all("isbn" in book for book in data)
    assert all("copies_available" in book for book in data) 