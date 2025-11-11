"""
Main FastAPI Application

KHÁI NIỆM:
- FastAPI instance = Application chính
- Middleware = Code chạy trước/sau mỗi request
- CORS = Cho phép frontend từ domain khác gọi API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.api import api_router
from app.db.session import engine, Base

# Create database tables
# VÍ DỤ: Tạo tables users, user_activities nếu chưa tồn tại
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",  # Swagger UI tại http://localhost:8000/docs
    redoc_url="/redoc",  # ReDoc tại http://localhost:8000/redoc
)

# CORS Middleware
# VÍ DỤ USE CASE:
# Frontend chạy tại http://localhost:3000 cần gọi API tại http://localhost:8000
# CORS cho phép cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Đổi thành specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """
    Root endpoint

    VÍ DỤ:
    GET http://localhost:8000/

    RESPONSE:
    {
        "message": "Welcome to User Management Service",
        "docs": "/docs",
        "version": "1.0"
    }
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0",
        "api_endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "users": f"{settings.API_V1_STR}/users",
            "activities": f"{settings.API_V1_STR}/users/{{user_id}}/activities"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint

    VÍ DỤ USE CASE:
    - Load balancer check
    - Monitoring tools
    - Docker health check

    RESPONSE: {"status": "healthy"}
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    # Run với: python app/main.py
    # Hoặc: uvicorn app.main:app --reload
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
