"""
Script tạo admin user

CÁCH SỬ DỤNG:
python create_admin.py

Hoặc với custom thông tin:
python create_admin.py --email admin@example.com --password admin123 --name "Admin User"
"""

import sys
import argparse
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash


def create_admin_user(
    email: str = "admin@admin.com",
    password: str = "admin123",
    full_name: str = "Admin User",
    country: str = "VN"
):
    """
    Tạo admin user

    VÍ DỤ:
    create_admin_user(
        email="admin@example.com",
        password="securepassword",
        full_name="Super Admin"
    )
    """
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == email).first()
        if existing_admin:
            print(f"❌ Admin user với email '{email}' đã tồn tại!")
            print(f"   ID: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Is Superuser: {existing_admin.is_superuser}")
            return None

        # Create admin user
        admin_user = User(
            email=email,
            full_name=full_name,
            hashed_password=get_password_hash(password),
            is_active=True,
            is_superuser=True,  # ← ADMIN FLAG
            country=country,
            bio="System Administrator"
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Tạo admin user thành công!")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Password: {password}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        print(f"\n🔑 Bạn có thể login với:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")

        return admin_user

    except Exception as e:
        print(f"❌ Lỗi khi tạo admin user: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def main():
    """
    Main function với argument parsing
    """
    parser = argparse.ArgumentParser(description="Tạo admin user cho hệ thống")
    parser.add_argument(
        "--email",
        type=str,
        default="admin@admin.com",
        help="Email của admin (default: admin@admin.com)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="admin123",
        help="Password của admin (default: admin123)"
    )
    parser.add_argument(
        "--name",
        type=str,
        default="Admin User",
        help="Tên đầy đủ của admin (default: Admin User)"
    )
    parser.add_argument(
        "--country",
        type=str,
        default="VN",
        help="Mã quốc gia (default: VN)"
    )

    args = parser.parse_args()

    print("🚀 Tạo admin user...")
    print(f"   Email: {args.email}")
    print(f"   Name: {args.name}")
    print(f"   Country: {args.country}")
    print()

    create_admin_user(
        email=args.email,
        password=args.password,
        full_name=args.name,
        country=args.country
    )


if __name__ == "__main__":
    main()
