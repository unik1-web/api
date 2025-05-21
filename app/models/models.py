# Импорт необходимых компонентов SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """
    Модель пользователя (библиотекаря).
    Хранит информацию о пользователях системы.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)  # Уникальный email пользователя
    hashed_password = Column(String)  # Хешированный пароль
    is_active = Column(Boolean, default=True)  # Статус активности пользователя
    is_superuser = Column(Boolean, default=False)  # Флаг суперпользователя
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Дата создания
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Дата обновления

class Book(Base):
    """
    Модель книги.
    Хранит информацию о книгах в библиотеке.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # Название книги
    author = Column(String, index=True)  # Автор книги
    isbn = Column(String, unique=True, index=True)  # Уникальный ISBN
    description = Column(String, nullable=True)  # Описание книги
    copies_available = Column(Integer, default=1)  # Количество доступных экземпляров
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Дата добавления
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Дата обновления

class Reader(Base):
    """
    Модель читателя.
    Хранит информацию о читателях библиотеки.
    """
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Имя читателя
    email = Column(String, unique=True, index=True)  # Уникальный email читателя
    phone = Column(String, nullable=True)  # Телефон читателя
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Дата регистрации
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Дата обновления

class BorrowedBook(Base):
    """
    Модель выданной книги.
    Хранит информацию о выдаче книг читателям.
    """
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))  # Ссылка на книгу
    reader_id = Column(Integer, ForeignKey("readers.id"))  # Ссылка на читателя
    borrowed_at = Column(DateTime(timezone=True), server_default=func.now())  # Дата выдачи
    returned_at = Column(DateTime(timezone=True), nullable=True)  # Дата возврата
    due_date = Column(DateTime(timezone=True))  # Срок возврата

    # Связи с другими таблицами
    book = relationship("Book")
    reader = relationship("Reader") 