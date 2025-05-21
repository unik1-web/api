from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Book, Reader, BorrowedBook, User
from app.schemas.borrow import BorrowedBook as BorrowedBookSchema, BorrowedBookCreate

router = APIRouter()

@router.post("/", response_model=BorrowedBookSchema)
def borrow_book(
    borrow: BorrowedBookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем существование книги и читателя
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    reader = db.query(Reader).filter(Reader.id == borrow.reader_id).first()
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    # Проверяем доступность книги
    if book.copies_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available"
        )
    
    # Проверяем, не заимствована ли уже книга этим читателем
    existing_borrow = db.query(BorrowedBook).filter(
        BorrowedBook.book_id == borrow.book_id,
        BorrowedBook.reader_id == borrow.reader_id,
        BorrowedBook.returned_at == None
    ).first()
    
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reader has already borrowed this book"
        )
    
    # Проверяем количество книг у читателя
    active_borrows = db.query(BorrowedBook).filter(
        BorrowedBook.reader_id == reader.id,
        BorrowedBook.returned_at == None
    ).count()
    
    if active_borrows >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reader has reached the maximum number of borrowed books"
        )
    
    # Создаем запись о выдаче
    db_borrow = BorrowedBook(**borrow.model_dump())
    db.add(db_borrow)
    
    # Уменьшаем количество доступных экземпляров
    book.copies_available -= 1
    
    db.commit()
    db.refresh(db_borrow)
    return db_borrow

@router.post("/return/{borrow_id}")
def return_book(
    borrow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_borrow = db.query(BorrowedBook).filter(BorrowedBook.id == borrow_id).first()
    if not db_borrow:
        raise HTTPException(status_code=404, detail="Borrow record not found")
    
    if db_borrow.returned_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has already been returned"
        )
    
    # Обновляем запись о выдаче
    db_borrow.returned_at = datetime.utcnow()
    
    # Увеличиваем количество доступных экземпляров
    book = db.query(Book).filter(Book.id == db_borrow.book_id).first()
    book.copies_available += 1
    
    db.commit()
    return {"message": "Book returned successfully"}

@router.get("/reader/{reader_id}", response_model=List[BorrowedBookSchema])
def get_reader_borrows(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if not reader:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    borrows = db.query(BorrowedBook).filter(
        BorrowedBook.reader_id == reader_id,
        BorrowedBook.returned_at == None
    ).all()
    
    return borrows

@router.get("/", response_model=List[BorrowedBookSchema])
def get_all_borrows(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all borrows with pagination.
    """
    borrows = db.query(BorrowedBook).offset(skip).limit(limit).all()
    return borrows 