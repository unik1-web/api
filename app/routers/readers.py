from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_user
from app.database import get_db
from app.models.models import Reader, User
from app.schemas.schemas import Reader as ReaderSchema, ReaderCreate

router = APIRouter()

@router.post("/", response_model=ReaderSchema)
def create_reader(
    reader: ReaderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reader = db.query(Reader).filter(Reader.email == reader.email).first()
    if db_reader:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    db_reader = Reader(**reader.model_dump())
    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    return db_reader

@router.get("/", response_model=List[ReaderSchema])
def read_readers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    readers = db.query(Reader).offset(skip).limit(limit).all()
    return readers

@router.get("/{reader_id}", response_model=ReaderSchema)
def read_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    return db_reader

@router.put("/{reader_id}", response_model=ReaderSchema)
def update_reader(
    reader_id: int,
    reader: ReaderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    for key, value in reader.model_dump().items():
        setattr(db_reader, key, value)
    
    db.commit()
    db.refresh(db_reader)
    return db_reader

@router.delete("/{reader_id}")
def delete_reader(
    reader_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_reader = db.query(Reader).filter(Reader.id == reader_id).first()
    if db_reader is None:
        raise HTTPException(status_code=404, detail="Reader not found")
    
    db.delete(db_reader)
    db.commit()
    return {"message": "Reader deleted successfully"} 