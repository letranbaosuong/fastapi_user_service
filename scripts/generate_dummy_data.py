"""
Generate Dummy Data Script

CHỨC NĂNG:
- Tạo 20,000+ users
- Tạo 5,000 projects
- Tạo 100,000+ user activities
- Tạo 50,000+ user-project relationships

TỔNG: ~175,000+ rows

CÁCH CHẠY:
python scripts/generate_dummy_data.py

LƯU Ý:
- Cần cài đặt: pip install faker
- Đảm bảo database đã start: docker-compose up -d
- Script tự động batch insert để tăng tốc độ
"""

import sys
import os
from pathlib import Path

# Add parent directory to path để import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
import random
from faker import Faker
from sqlalchemy.orm import Session
from tqdm import tqdm

from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.models.user_activity import UserActivity
from app.models.project import Project, user_projects
from app.core.security import get_password_hash


# Initialize Faker với multiple locales
fake = Faker(['en_US', 'vi_VN', 'ja_JP', 'ko_KR', 'fr_FR'])

# Constants
NUM_USERS = 20000
NUM_PROJECTS = 5000
NUM_ACTIVITIES_PER_USER = 5  # Average
NUM_MEMBERSHIPS_PER_USER = 3  # Average projects per user

# Batch size for bulk insert (tăng tốc độ)
BATCH_SIZE = 1000

# Countries (ISO 3166-1 alpha-2)
COUNTRIES = ['VN', 'US', 'JP', 'KR', 'FR', 'GB', 'DE', 'CN', 'IN', 'BR', 'AU', 'CA', 'TH', 'SG', 'MY']

# Activity types
ACTION_TYPES = ['LOGIN', 'LOGOUT', 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'DOWNLOAD', 'UPLOAD']

# Project statuses
PROJECT_STATUSES = ['planning', 'in_progress', 'completed', 'on_hold', 'cancelled']

# User roles in projects
USER_ROLES = ['owner', 'admin', 'member']


def create_tables():
    """Tạo tất cả tables nếu chưa tồn tại"""
    print("📋 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully\n")


def clear_existing_data(db: Session):
    """Xóa data cũ (optional - dùng khi test)"""
    response = input("⚠️  Clear existing data? (yes/no): ")
    if response.lower() == 'yes':
        print("🗑️  Clearing existing data...")
        db.execute(user_projects.delete())
        db.query(UserActivity).delete()
        db.query(Project).delete()
        db.query(User).delete()
        db.commit()
        print("✅ Existing data cleared\n")
    else:
        print("⏭️  Skipping data clearing\n")


def generate_users(db: Session, num_users: int) -> list:
    """
    Generate dummy users

    VÍ DỤ DATA:
    - email: john.doe12345@example.com
    - full_name: John Doe
    - country: VN, US, JP, ...
    - bio: Random bio text
    """
    print(f"👥 Generating {num_users:,} users...")

    # OPTIMIZATION: Hash password once and reuse (same password for all test users)
    print("🔐 Hashing password (one time)...")
    hashed_password = get_password_hash("password123")

    users = []
    used_emails = set()

    # Progress bar
    with tqdm(total=num_users, desc="Users", unit="user") as pbar:
        batch = []

        for i in range(num_users):
            # Generate unique email
            while True:
                email = fake.unique.email()
                if email not in used_emails:
                    used_emails.add(email)
                    break

            # Random country
            country = random.choice(COUNTRIES)

            # Random bio (50% chance of having bio)
            bio = fake.text(max_nb_chars=200) if random.random() > 0.5 else None

            # Random timestamps (within last 2 years)
            created_at = fake.date_time_between(start_date='-2y', end_date='now')

            user = User(
                email=email,
                full_name=fake.name(),
                hashed_password=hashed_password,  # Reuse hashed password (same for all)
                is_active=random.choice([True, True, True, False]),  # 75% active
                is_superuser=random.choice([True, False, False, False, False]),  # 20% superuser
                bio=bio,
                country=country,
                created_at=created_at,
            )

            batch.append(user)
            users.append(user)

            # Bulk insert khi đủ batch size
            if len(batch) >= BATCH_SIZE:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
                pbar.update(BATCH_SIZE)

        # Insert remaining users
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            pbar.update(len(batch))

    # Refresh để get IDs
    print("🔄 Refreshing user IDs...")
    user_ids = [user.id for user in db.query(User).all()]
    print(f"✅ Created {len(user_ids):,} users\n")

    return user_ids


def generate_projects(db: Session, num_projects: int, user_ids: list) -> list:
    """
    Generate dummy projects

    VÍ DỤ DATA:
    - name: E-commerce Platform Redesign
    - description: Complete overhaul of the e-commerce platform...
    - status: planning, in_progress, completed, ...
    """
    print(f"📁 Generating {num_projects:,} projects...")

    projects = []

    # Progress bar
    with tqdm(total=num_projects, desc="Projects", unit="project") as pbar:
        batch = []

        for i in range(num_projects):
            # Random project name
            project_types = [
                'Website', 'Mobile App', 'API', 'Dashboard', 'Platform',
                'System', 'Tool', 'Service', 'Portal', 'Application'
            ]
            actions = [
                'Development', 'Redesign', 'Migration', 'Upgrade',
                'Implementation', 'Integration', 'Optimization'
            ]

            name = f"{random.choice(project_types)} {random.choice(actions)} {i+1}"
            description = fake.paragraph(nb_sentences=3)

            # Random status
            status = random.choice(PROJECT_STATUSES)

            # Random dates
            created_at = fake.date_time_between(start_date='-2y', end_date='now')
            start_date = created_at + timedelta(days=random.randint(1, 30))

            # End date (only for completed/cancelled projects)
            end_date = None
            if status in ['completed', 'cancelled']:
                end_date = start_date + timedelta(days=random.randint(30, 365))

            project = Project(
                name=name,
                description=description,
                is_active=status in ['planning', 'in_progress'],
                status=status,
                start_date=start_date,
                end_date=end_date,
                created_at=created_at,
            )

            batch.append(project)
            projects.append(project)

            # Bulk insert
            if len(batch) >= BATCH_SIZE:
                db.bulk_save_objects(batch)
                db.commit()
                batch = []
                pbar.update(BATCH_SIZE)

        # Insert remaining
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            pbar.update(len(batch))

    # Get project IDs
    print("🔄 Refreshing project IDs...")
    project_ids = [project.id for project in db.query(Project).all()]
    print(f"✅ Created {len(project_ids):,} projects\n")

    return project_ids


def generate_user_activities(db: Session, user_ids: list):
    """
    Generate dummy user activities

    VÍ DỤ DATA:
    - action_type: LOGIN, LOGOUT, CREATE, UPDATE, ...
    - description: User logged in from Chrome
    - ip_address: 192.168.1.100
    """
    num_activities = NUM_USERS * NUM_ACTIVITIES_PER_USER
    print(f"📊 Generating ~{num_activities:,} user activities...")

    # Progress bar
    with tqdm(total=num_activities, desc="Activities", unit="activity") as pbar:
        batch = []
        count = 0

        for user_id in user_ids:
            # Random number of activities per user (0-10)
            num_user_activities = random.randint(0, 10)

            for _ in range(num_user_activities):
                action_type = random.choice(ACTION_TYPES)

                # Generate description based on action type
                descriptions = {
                    'LOGIN': [f"User logged in from {fake.user_agent()}", "Successful login"],
                    'LOGOUT': ["User logged out", "Session ended"],
                    'CREATE': [f"Created {fake.word()}", "New item created"],
                    'UPDATE': [f"Updated {fake.word()}", "Item modified"],
                    'DELETE': [f"Deleted {fake.word()}", "Item removed"],
                    'VIEW': [f"Viewed {fake.word()} page", "Page accessed"],
                    'DOWNLOAD': [f"Downloaded {fake.file_name()}", "File downloaded"],
                    'UPLOAD': [f"Uploaded {fake.file_name()}", "File uploaded"],
                }

                description = random.choice(descriptions.get(action_type, ["Activity performed"]))

                # Random IP address
                ip_address = fake.ipv4()

                # Random user agent
                user_agent = fake.user_agent()

                # Random timestamp (within user's lifetime)
                created_at = fake.date_time_between(start_date='-2y', end_date='now')

                activity = UserActivity(
                    user_id=user_id,
                    action_type=action_type,
                    description=description,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    created_at=created_at,
                )

                batch.append(activity)
                count += 1

                # Bulk insert
                if len(batch) >= BATCH_SIZE:
                    db.bulk_save_objects(batch)
                    db.commit()
                    batch = []
                    pbar.update(BATCH_SIZE)

        # Insert remaining
        if batch:
            db.bulk_save_objects(batch)
            db.commit()
            pbar.update(len(batch))

    print(f"✅ Created {count:,} user activities\n")


def generate_user_project_memberships(db: Session, user_ids: list, project_ids: list):
    """
    Generate user-project relationships (many-to-many)

    VÍ DỤ DATA:
    - user_id: 1
    - project_id: 5
    - role: owner, admin, member
    """
    num_memberships = NUM_USERS * NUM_MEMBERSHIPS_PER_USER
    print(f"🔗 Generating ~{num_memberships:,} user-project memberships...")

    # Progress bar
    with tqdm(total=num_memberships, desc="Memberships", unit="membership") as pbar:
        count = 0
        used_pairs = set()  # Track (user_id, project_id) to avoid duplicates

        for user_id in user_ids:
            # Random number of projects per user (1-6)
            num_user_projects = random.randint(1, 6)

            # Select random projects
            selected_projects = random.sample(project_ids, min(num_user_projects, len(project_ids)))

            for project_id in selected_projects:
                # Avoid duplicates
                if (user_id, project_id) in used_pairs:
                    continue

                used_pairs.add((user_id, project_id))

                # Random role (more members than owners/admins)
                role = random.choices(
                    USER_ROLES,
                    weights=[5, 15, 80],  # 5% owner, 15% admin, 80% member
                    k=1
                )[0]

                # Random join date
                joined_at = fake.date_time_between(start_date='-2y', end_date='now')

                # Insert using raw SQL for association table
                db.execute(
                    user_projects.insert().values(
                        user_id=user_id,
                        project_id=project_id,
                        role=role,
                        joined_at=joined_at
                    )
                )

                count += 1

                # Commit batch
                if count % BATCH_SIZE == 0:
                    db.commit()
                    pbar.update(BATCH_SIZE)

        # Final commit
        db.commit()
        pbar.update(count % BATCH_SIZE)

    print(f"✅ Created {count:,} user-project memberships\n")


def print_statistics(db: Session):
    """Print final statistics"""
    print("\n" + "="*60)
    print("📈 DATABASE STATISTICS")
    print("="*60)

    users_count = db.query(User).count()
    projects_count = db.query(Project).count()
    activities_count = db.query(UserActivity).count()
    memberships_count = db.execute(user_projects.select()).fetchall()

    print(f"👥 Users:              {users_count:,}")
    print(f"📁 Projects:           {projects_count:,}")
    print(f"📊 User Activities:    {activities_count:,}")
    print(f"🔗 Memberships:        {len(memberships_count):,}")
    print(f"➕ TOTAL ROWS:         {users_count + projects_count + activities_count + len(memberships_count):,}")
    print("="*60)

    # Additional stats
    print("\n📊 Additional Statistics:")
    active_users = db.query(User).filter(User.is_active == True).count()
    superusers = db.query(User).filter(User.is_superuser == True).count()
    active_projects = db.query(Project).filter(Project.is_active == True).count()

    print(f"  ✅ Active Users:     {active_users:,} ({active_users/users_count*100:.1f}%)")
    print(f"  👑 Superusers:       {superusers:,} ({superusers/users_count*100:.1f}%)")
    print(f"  🚀 Active Projects:  {active_projects:,} ({active_projects/projects_count*100:.1f}%)")
    print("="*60 + "\n")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("🚀 DUMMY DATA GENERATOR")
    print("="*60 + "\n")

    # Create tables
    create_tables()

    # Create database session
    db = SessionLocal()

    try:
        # Clear existing data (optional)
        clear_existing_data(db)

        # Start time
        start_time = datetime.now()
        print(f"⏰ Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Generate data
        user_ids = generate_users(db, NUM_USERS)
        project_ids = generate_projects(db, NUM_PROJECTS, user_ids)
        generate_user_activities(db, user_ids)
        generate_user_project_memberships(db, user_ids, project_ids)

        # End time
        end_time = datetime.now()
        duration = end_time - start_time

        print(f"⏰ End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Duration: {duration}\n")

        # Print statistics
        print_statistics(db)

        print("✅ Dummy data generated successfully!")
        print(f"🎉 Ready to test with {NUM_USERS:,}+ rows!\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
