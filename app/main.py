from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, books, readers, borrows
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Library API", description="RESTful API for library management")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Включаем роутеры
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(readers.router, prefix="/readers", tags=["readers"])
app.include_router(borrows.router, prefix="/borrows", tags=["borrows"])

@app.get("/")
async def root():
    return {"message": "Welcome to Library API"} 