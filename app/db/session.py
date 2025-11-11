"""
Database Session Management

KHÁI NIỆM:
1. Engine: Connection pool tới database
2. SessionLocal: Factory tạo database sessions
3. Base: Base class cho tất cả models

VÍ DỤ WORKFLOW:
Request -> get_db() tạo session -> Xử lý -> Close session
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Tạo Database Engine
# VÍ DỤ: postgresql://user:pass@localhost:5432/dbname
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Check connection trước khi dùng
    echo=settings.DEBUG  # Log SQL queries trong debug mode
)

# Session Factory
# VÍ DỤ: Mỗi request tạo một session mới
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class cho models
Base = declarative_base()


def get_db():
    """
    Dependency Injection cho Database Session

    KHÁI NIỆM: FastAPI tự động gọi function này và inject session vào route

    VÍ DỤ SỬ DỤNG:
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        # db là session được inject tự động
        return db.query(User).all()

    WORKFLOW:
    1. Tạo session
    2. Yield session cho route handler
    3. Close session sau khi xong (even if error)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
