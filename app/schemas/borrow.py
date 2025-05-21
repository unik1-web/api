from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BorrowedBookBase(BaseModel):
    book_id: int
    reader_id: int
    due_date: datetime

class BorrowedBookCreate(BorrowedBookBase):
    pass

class BorrowedBookInDBBase(BorrowedBookBase):
    id: int
    borrowed_at: datetime
    returned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BorrowedBook(BorrowedBookInDBBase):
    pass

class BorrowedBookInDB(BorrowedBookInDBBase):
    pass 