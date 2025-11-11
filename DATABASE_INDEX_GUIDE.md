# Database Index Guide - Tối Ưu Tốc Độ Truy Vấn

## Khái niệm Index

**Index** giống như mục lục trong sách - giúp database tìm data nhanh hơn mà không cần scan toàn bộ table.

### Single Column Index vs Composite Index

```python
# Single column index (1 cột)
Column('email', String, index=True)  # Index trên email

# Composite index (2-3 cột)
Index('idx_user_country_active', 'country', 'is_active')  # Index trên country + is_active
```

## 1. Composite Index trong SQLAlchemy

### Cú pháp cơ bản

```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    country = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime)

    # Composite index: 2 cột
    __table_args__ = (
        Index('idx_country_active', 'country', 'is_active'),
    )
```

### Multiple Composite Indexes

```python
class User(Base):
    __tablename__ = "users"

    # ... columns ...

    # Multiple indexes
    __table_args__ = (
        # Index 2 cột
        Index('idx_country_active', 'country', 'is_active'),

        # Index 3 cột
        Index('idx_country_active_created', 'country', 'is_active', 'created_at'),

        # Index với DESC (giảm dần)
        Index('idx_created_desc', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )
```

## 2. Khi Nào Nên Dùng Composite Index?

### ✅ Nên dùng khi:

#### A. Query thường WHERE với nhiều điều kiện

```python
# Query: Tìm users active ở Vietnam
users = db.query(User).filter(
    User.country == 'VN',
    User.is_active == True
).all()

# → Nên tạo index: ('country', 'is_active')
```

#### B. Query với ORDER BY

```python
# Query: Lấy users mới nhất ở US
users = db.query(User).filter(
    User.country == 'US'
).order_by(User.created_at.desc()).all()

# → Nên tạo index: ('country', 'created_at')
```

#### C. JOIN conditions

```python
# Query: Join users với activities
results = db.query(User, UserActivity).join(
    UserActivity,
    and_(
        UserActivity.user_id == User.id,
        UserActivity.action_type == 'LOGIN'
    )
).all()

# → Nên tạo index: ('user_id', 'action_type') trên user_activities
```

### ❌ KHÔNG nên dùng khi:

1. Table nhỏ (< 1000 rows)
2. Column có ít giá trị unique (cardinality thấp)
3. Frequently updated columns
4. Table có nhiều INSERT/UPDATE (index làm chậm writes)

## 3. Thứ Tự Cột Trong Composite Index

**QUY TẮC QUAN TRỌNG**: Thứ tự cột ảnh hưởng đến performance!

### Left-to-Right Rule

```python
# Index: ('country', 'is_active', 'created_at')

# ✅ Sử dụng được index (bắt đầu từ trái)
WHERE country = 'VN'
WHERE country = 'VN' AND is_active = True
WHERE country = 'VN' AND is_active = True AND created_at > '2024-01-01'

# ❌ KHÔNG sử dụng được index (không bắt đầu từ trái)
WHERE is_active = True
WHERE created_at > '2024-01-01'
WHERE is_active = True AND created_at > '2024-01-01'
```

### Best Practice: Sắp xếp cột

```
1. Equality conditions (=) trước
2. Range conditions (>, <, BETWEEN) sau
3. ORDER BY columns cuối cùng
```

**Ví dụ đúng**:
```python
Index('idx_optimal',
    'country',      # 1. Equality: country = 'VN'
    'is_active',    # 2. Equality: is_active = True
    'created_at'    # 3. Range: created_at > '2024-01-01'
)
```

## 4. Ví Dụ Thực Tế Cho Project

### A. User Model - Tối Ưu

```python
# app/models/user.py
from sqlalchemy import Index, text

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    country = Column(String(2), nullable=True)

    # Composite indexes
    __table_args__ = (
        # 1. Tìm active users theo country
        Index('idx_country_active', 'country', 'is_active'),

        # 2. Lọc users mới theo country
        Index('idx_country_created', 'country', 'created_at'),

        # 3. Admin dashboard: active users + role
        Index('idx_active_superuser', 'is_active', 'is_superuser'),

        # 4. Search users gần đây
        Index('idx_active_created_desc', 'is_active', text('created_at DESC')),
    )
```

### B. UserActivity Model - Tối Ưu

```python
# app/models/user_activity.py
class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite indexes
    __table_args__ = (
        # 1. Xem activities của 1 user
        Index('idx_user_created', 'user_id', 'created_at'),

        # 2. Filter by action type cho 1 user
        Index('idx_user_action_created', 'user_id', 'action_type', 'created_at'),

        # 3. Security: Track login attempts by IP
        Index('idx_action_ip_created', 'action_type', 'ip_address', 'created_at'),
    )
```

### C. Project Model - Tối Ưu

```python
# app/models/project.py
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="planning")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite indexes
    __table_args__ = (
        # 1. Dashboard: Active projects by status
        Index('idx_active_status', 'is_active', 'status'),

        # 2. Recent projects by status
        Index('idx_status_created', 'status', 'created_at'),

        # 3. Active + recent projects
        Index('idx_active_created_desc', 'is_active', text('created_at DESC')),
    )
```

### D. User-Project Association - Tối Ưu

```python
# app/models/project.py
user_projects = Table(
    "user_projects",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("project_id", Integer, ForeignKey("projects.id"), nullable=False),
    Column("role", String(50), default="member"),
    Column("joined_at", DateTime(timezone=True), server_default=func.now()),

    # Composite indexes
    Index('idx_user_project', 'user_id', 'project_id'),  # Unique membership
    Index('idx_project_role', 'project_id', 'role'),     # Get members by role
    Index('idx_user_joined', 'user_id', 'joined_at'),    # User's project timeline
)
```

## 5. Tạo Index Với Alembic Migration

### Tạo Migration File

```bash
# Tạo migration mới
alembic revision -m "add composite indexes"
```

### Migration Code

```python
# alembic/versions/xxx_add_composite_indexes.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Users table indexes
    op.create_index('idx_country_active', 'users', ['country', 'is_active'])
    op.create_index('idx_country_created', 'users', ['country', 'created_at'])
    op.create_index('idx_active_superuser', 'users', ['is_active', 'is_superuser'])

    # User activities indexes
    op.create_index('idx_user_created', 'user_activities', ['user_id', 'created_at'])
    op.create_index('idx_user_action_created', 'user_activities',
                    ['user_id', 'action_type', 'created_at'])

    # Projects indexes
    op.create_index('idx_active_status', 'projects', ['is_active', 'status'])
    op.create_index('idx_status_created', 'projects', ['status', 'created_at'])

    # User-projects indexes
    op.create_index('idx_user_project', 'user_projects', ['user_id', 'project_id'])
    op.create_index('idx_project_role', 'user_projects', ['project_id', 'role'])

def downgrade():
    # Users
    op.drop_index('idx_country_active', 'users')
    op.drop_index('idx_country_created', 'users')
    op.drop_index('idx_active_superuser', 'users')

    # User activities
    op.drop_index('idx_user_created', 'user_activities')
    op.drop_index('idx_user_action_created', 'user_activities')

    # Projects
    op.drop_index('idx_active_status', 'projects')
    op.drop_index('idx_status_created', 'projects')

    # User-projects
    op.drop_index('idx_user_project', 'user_projects')
    op.drop_index('idx_project_role', 'user_projects')
```

### Apply Migration

```bash
# Chạy migration
alembic upgrade head
```

## 6. Kiểm Tra Index Performance

### A. Xem danh sách indexes

```sql
-- PostgreSQL
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
```

### B. Analyze query performance

```sql
-- Bật query analysis
EXPLAIN ANALYZE
SELECT * FROM users
WHERE country = 'VN'
  AND is_active = true;

-- Kết quả mẫu:
-- Index Scan using idx_country_active on users  (cost=0.29..8.31 rows=1 width=100)
--   Index Cond: ((country = 'VN') AND (is_active = true))
```

### C. Check index usage

```sql
-- PostgreSQL: Xem index nào được sử dụng nhiều
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### D. Find unused indexes

```sql
-- Tìm indexes không được dùng (có thể xóa)
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE 'pg_%';
```

## 7. Best Practices

### ✅ DO:

1. **Analyze queries trước khi tạo index**
   ```python
   # Dùng logging để xem queries nào chậm
   import logging
   logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   ```

2. **Test performance với data thực**
   ```bash
   # Generate dummy data để test
   python scripts/generate_dummy_data.py
   ```

3. **Monitor index usage**
   ```sql
   -- Check định kỳ
   SELECT * FROM pg_stat_user_indexes;
   ```

4. **Use EXPLAIN ANALYZE**
   ```sql
   EXPLAIN ANALYZE SELECT ...;
   ```

### ❌ DON'T:

1. **Không tạo quá nhiều indexes**
   - Mỗi index chiếm storage
   - Làm chậm INSERT/UPDATE/DELETE
   - Rule of thumb: < 5 indexes per table

2. **Không index columns với low cardinality**
   ```python
   # BAD: Boolean chỉ có 2 giá trị (True/False)
   Index('idx_active', 'is_active')  # ❌

   # GOOD: Combine với column khác
   Index('idx_country_active', 'country', 'is_active')  # ✅
   ```

3. **Không index quá nhiều cột (> 3-4)**
   ```python
   # TOO MANY COLUMNS
   Index('idx_too_many', 'col1', 'col2', 'col3', 'col4', 'col5')  # ❌
   ```

## 8. Covering Index (Advanced)

**Covering index** chứa tất cả columns cần thiết cho query → không cần access table.

```python
# PostgreSQL: Include columns
from sqlalchemy.dialects.postgresql import ARRAY

Index('idx_user_covering',
    'country', 'is_active',
    postgresql_include=['full_name', 'email']  # Include thêm columns
)

# Query này KHÔNG cần access table
# SELECT full_name, email
# FROM users
# WHERE country = 'VN' AND is_active = true;
```

## 9. Partial Index (Filtered Index)

Index chỉ một phần data → nhỏ hơn, nhanh hơn.

```python
from sqlalchemy import text

# Chỉ index active users
Index('idx_active_users', 'email',
    postgresql_where=text('is_active = true')
)

# Chỉ index recent data (30 ngày gần nhất)
Index('idx_recent_activities', 'user_id', 'created_at',
    postgresql_where=text("created_at >= NOW() - INTERVAL '30 days'")
)
```

## 10. Performance Testing Script

```python
# scripts/test_index_performance.py
import time
from sqlalchemy import create_engine, text
from app.db.session import SessionLocal

def test_query_performance():
    db = SessionLocal()

    # Test 1: Without index
    start = time.time()
    result = db.execute(text("""
        SELECT * FROM users
        WHERE country = 'VN' AND is_active = true
    """))
    duration_no_index = time.time() - start

    print(f"Without composite index: {duration_no_index:.4f}s")

    # Create index
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_country_active
        ON users (country, is_active)
    """))
    db.commit()

    # Test 2: With index
    start = time.time()
    result = db.execute(text("""
        SELECT * FROM users
        WHERE country = 'VN' AND is_active = true
    """))
    duration_with_index = time.time() - start

    print(f"With composite index: {duration_with_index:.4f}s")
    print(f"Improvement: {(duration_no_index/duration_with_index):.2f}x faster")

    db.close()

if __name__ == "__main__":
    test_query_performance()
```

## Tổng Kết

### Quick Reference

```python
# 1. Single column index
Column('email', String, index=True)

# 2. Composite index (2 cột)
Index('idx_country_active', 'country', 'is_active')

# 3. Composite index (3 cột)
Index('idx_country_active_created', 'country', 'is_active', 'created_at')

# 4. Index với DESC
Index('idx_created_desc', text('created_at DESC'))

# 5. Unique composite index
Index('idx_user_project_unique', 'user_id', 'project_id', unique=True)

# 6. Partial index (PostgreSQL)
Index('idx_active_only', 'email', postgresql_where=text('is_active = true'))
```

### Khi Nào Cần Index?

- WHERE clause thường xuyên
- JOIN conditions
- ORDER BY columns
- GROUP BY columns
- Foreign keys

### Performance Metrics

- **Small table** (< 1K rows): Index ít ảnh hưởng
- **Medium table** (1K-100K rows): Index cải thiện 10-100x
- **Large table** (> 100K rows): Index cải thiện 100-1000x

---

**Next Steps**:
1. Analyze queries trong application
2. Tạo migration file với indexes phù hợp
3. Test performance với dummy data (194K+ rows)
4. Monitor index usage với pg_stat_user_indexes
