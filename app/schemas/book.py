from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    description: Optional[str] = None
    copies_available: int = 1

class BookCreate(BookBase):
    pass

class BookUpdate(BookBase):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    copies_available: Optional[int] = None

class BookInDBBase(BookBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Book(BookInDBBase):
    pass

class BookInDB(BookInDBBase):
    pass 