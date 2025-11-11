# Hướng Dẫn Generate Dummy Data & pgAdmin4

## Tổng Quan

Script generate **175,000+ rows** dummy data realistic để test performance, cache, và các features.

### Breakdown Data:
- **20,000 users** - Đa dạng countries, bios, roles
- **5,000 projects** - Các status khác nhau (planning, in_progress, completed, ...)
- **100,000+ user activities** - LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, ...
- **50,000+ user-project memberships** - Many-to-many relationships với roles

**TỔNG: ~175,000+ rows**

## Prerequisites

### 1. Install Dependencies

```bash
# Install Faker and tqdm
pip install faker==22.0.0 tqdm==4.66.1

# Hoặc install tất cả dependencies
pip install -r requirements.txt
```

### 2. Start Database

```bash
# Start PostgreSQL, Redis, và pgAdmin4
docker-compose up -d

# Check services are running
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE                  STATUS
xxx            postgres:15-alpine     Up
xxx            redis:7-alpine         Up
xxx            dpage/pgadmin4         Up
```

## Generate Dummy Data

### Quick Start

```bash
# Chạy script (từ project root)
python scripts/generate_dummy_data.py
```

### Script Workflow

```
1. Create database tables (nếu chưa tồn tại)
2. Clear existing data? (yes/no)
   ⚠️  yes → Xóa tất cả data cũ
   ⏭️  no  → Giữ data cũ, thêm data mới
3. Generate users (20,000) → ~30 seconds
4. Generate projects (5,000) → ~10 seconds
5. Generate activities (100,000+) → ~45 seconds
6. Generate memberships (50,000+) → ~35 seconds
7. Print statistics

TOTAL TIME: ~2-3 minutes
```

### Example Output

```
============================================================
🚀 DUMMY DATA GENERATOR
============================================================

📋 Creating database tables...
✅ Tables created successfully

⚠️  Clear existing data? (yes/no): yes
🗑️  Clearing existing data...
✅ Existing data cleared

⏰ Start time: 2024-01-15 10:00:00

👥 Generating 20,000 users...
Users: 100%|████████████████████| 20000/20000 [00:28<00:00, 706.32user/s]
✅ Created 20,000 users

📁 Generating 5,000 projects...
Projects: 100%|██████████████████| 5000/5000 [00:09<00:00, 524.71project/s]
✅ Created 5,000 projects

📊 Generating ~100,000 user activities...
Activities: 100%|███████████████| 100000/100000 [00:42<00:00, 2341.56activity/s]
✅ Created 102,345 user activities

🔗 Generating ~60,000 user-project memberships...
Memberships: 100%|█████████████| 58230/58230 [00:31<00:00, 1853.22membership/s]
✅ Created 58,230 user-project memberships

⏰ End time: 2024-01-15 10:02:35
⏱️  Duration: 0:02:35

============================================================
📈 DATABASE STATISTICS
============================================================
👥 Users:              20,000
📁 Projects:           5,000
📊 User Activities:    102,345
🔗 Memberships:        58,230
➕ TOTAL ROWS:         185,575
============================================================

📊 Additional Statistics:
  ✅ Active Users:     14,987 (74.9%)
  👑 Superusers:       4,012 (20.1%)
  🚀 Active Projects:  2,998 (60.0%)
============================================================

✅ Dummy data generated successfully!
🎉 Ready to test with 185,575+ rows!
```

## Generated Data Details

### 1. Users (20,000 rows)

**Fields:**
- `email`: Unique, realistic emails (john.doe@example.com)
- `full_name`: Random names (John Doe, 山田太郎, Nguyễn Văn A, ...)
- `password`: All test users có password: `password123`
- `is_active`: 75% active, 25% inactive
- `is_superuser`: 20% superuser, 80% regular user
- `country`: VN, US, JP, KR, FR, GB, DE, CN, IN, BR, AU, CA, TH, SG, MY
- `bio`: 50% có bio text
- `created_at`: Random trong 2 năm qua

**Example:**
```json
{
  "id": 1,
  "email": "john.doe12345@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "country": "US",
  "bio": "Software engineer passionate about clean code...",
  "created_at": "2023-06-15T10:30:00Z"
}
```

### 2. Projects (5,000 rows)

**Fields:**
- `name`: "Website Development 1", "Mobile App Redesign 42", ...
- `description`: Realistic project descriptions
- `status`: planning, in_progress, completed, on_hold, cancelled
- `is_active`: Active cho planning/in_progress projects
- `start_date`: Random dates
- `end_date`: Chỉ cho completed/cancelled projects
- `created_at`: Random trong 2 năm qua

**Example:**
```json
{
  "id": 1,
  "name": "E-commerce Platform Development 123",
  "description": "Complete overhaul of the e-commerce platform with modern UI/UX...",
  "status": "in_progress",
  "is_active": true,
  "start_date": "2023-07-01T00:00:00Z",
  "end_date": null,
  "created_at": "2023-06-20T00:00:00Z"
}
```

### 3. User Activities (100,000+ rows)

**Fields:**
- `user_id`: Reference to users table
- `action_type`: LOGIN, LOGOUT, CREATE, UPDATE, DELETE, VIEW, DOWNLOAD, UPLOAD
- `description`: Context-aware descriptions
- `ip_address`: Random IPv4 addresses
- `user_agent`: Realistic browser user agents
- `created_at`: Random timestamps

**Example:**
```json
{
  "id": 1,
  "user_id": 42,
  "action_type": "LOGIN",
  "description": "User logged in from Chrome",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
  "created_at": "2024-01-15T08:30:00Z"
}
```

### 4. User-Project Memberships (50,000+ rows)

**Fields:**
- `user_id`: Reference to users
- `project_id`: Reference to projects
- `role`: owner (5%), admin (15%), member (80%)
- `joined_at`: Random join dates

**Example:**
```json
{
  "id": 1,
  "user_id": 15,
  "project_id": 203,
  "role": "member",
  "joined_at": "2023-08-10T00:00:00Z"
}
```

## pgAdmin4 Usage

### Access pgAdmin4

**URL:** http://localhost:5050

**Login Credentials:**
- Email: `admin@admin.com`
- Password: `admin`

### Setup Server Connection (First Time)

1. Open http://localhost:5050
2. Login với credentials trên
3. Click **Add New Server**

#### General Tab:
- Name: `Local PostgreSQL`

#### Connection Tab:
- Host: `postgres` (container name trong Docker network)
- Port: `5432`
- Maintenance Database: `user_service_db`
- Username: `postgres`
- Password: `password`
- ☑️ Save password

4. Click **Save**

### View Data

#### Navigate to Tables:
```
Servers
└── Local PostgreSQL
    └── Databases
        └── user_service_db
            └── Schemas
                └── public
                    └── Tables
                        ├── users
                        ├── user_activities
                        ├── projects
                        └── user_projects
```

#### View Table Data:
1. Right-click on table (e.g., `users`)
2. Select **View/Edit Data** → **All Rows**
3. Browse data với pagination

### Useful Queries

#### Top 10 Most Active Users:
```sql
SELECT
    u.id,
    u.email,
    u.full_name,
    COUNT(ua.id) as activity_count
FROM users u
LEFT JOIN user_activities ua ON u.id = ua.user_id
GROUP BY u.id, u.email, u.full_name
ORDER BY activity_count DESC
LIMIT 10;
```

#### Projects by Status:
```sql
SELECT
    status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM projects), 2) as percentage
FROM projects
GROUP BY status
ORDER BY count DESC;
```

#### Users by Country:
```sql
SELECT
    country,
    COUNT(*) as user_count
FROM users
WHERE country IS NOT NULL
GROUP BY country
ORDER BY user_count DESC
LIMIT 10;
```

#### Active Projects with Member Count:
```sql
SELECT
    p.id,
    p.name,
    p.status,
    COUNT(up.user_id) as member_count
FROM projects p
LEFT JOIN user_projects up ON p.id = up.project_id
WHERE p.is_active = true
GROUP BY p.id, p.name, p.status
ORDER BY member_count DESC
LIMIT 20;
```

#### Activity Timeline (Last 24 hours):
```sql
SELECT
    action_type,
    COUNT(*) as count,
    DATE_TRUNC('hour', created_at) as hour
FROM user_activities
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY action_type, hour
ORDER BY hour DESC, count DESC;
```

## Performance Testing với Dummy Data

### Test Cache Performance

```bash
# Start Redis và server
docker-compose up -d
uvicorn app.main:app --reload

# Test without cache (first request)
time curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Expected: ~150-200ms (Cache MISS)

# Test with cache (second request)
time curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
# Expected: ~5-10ms (Cache HIT) - 20x faster!
```

### Test Pagination

```bash
# Page 1 (0-100)
GET /api/v1/users?skip=0&limit=100

# Page 2 (100-200)
GET /api/v1/users?skip=100&limit=100

# Page 200 (19900-20000)
GET /api/v1/users?skip=19900&limit=100
```

### Test Filters

```bash
# Filter by countries
GET /api/v1/users?countries=VN&countries=US&countries=JP

# Filter projects by status
GET /api/v1/projects?status=in_progress

# Get user's projects
GET /api/v1/projects/my-projects
```

### Load Testing với Apache Bench

```bash
# Install ab (Apache Bench)
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Test 1000 requests, 10 concurrent
ab -n 1000 -c 10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/users?skip=0&limit=100

# Results:
# - Requests per second
# - Time per request
# - Transfer rate
```

## Cleanup

### Clear All Dummy Data

```bash
# Option 1: Chạy lại script với clear data
python scripts/generate_dummy_data.py
# Chọn 'yes' khi hỏi clear data

# Option 2: Manual SQL
docker exec user_service_postgres psql -U postgres -d user_service_db <<EOF
TRUNCATE TABLE user_projects CASCADE;
TRUNCATE TABLE user_activities CASCADE;
TRUNCATE TABLE projects CASCADE;
TRUNCATE TABLE users CASCADE;
EOF
```

### Remove Docker Volumes

```bash
# Stop containers
docker-compose down

# Remove volumes (⚠️ Xóa tất cả data)
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Troubleshooting

### Issue 1: Script Fails with "No module named 'faker'"

**Solution:**
```bash
pip install faker tqdm
# Or
pip install -r requirements.txt
```

### Issue 2: Database Connection Error

**Check database is running:**
```bash
docker ps | grep postgres

# If not running:
docker-compose up -d postgres
```

### Issue 3: Slow Performance

**Solutions:**
1. Increase BATCH_SIZE trong script (default: 1000)
2. Disable foreign key checks temporarily (advanced)
3. Generate less data (giảm NUM_USERS, NUM_PROJECTS)

### Issue 4: pgAdmin4 Can't Connect

**Common fixes:**
1. Host: Use `postgres` (NOT `localhost`)
2. Port: `5432`
3. Username: `postgres`
4. Password: `password`
5. Database: `user_service_db`

## Advanced Features

### Customize Data Generation

Edit `scripts/generate_dummy_data.py`:

```python
# Số lượng data
NUM_USERS = 50000  # Tăng lên 50k users
NUM_PROJECTS = 10000  # Tăng lên 10k projects
NUM_ACTIVITIES_PER_USER = 10  # Tăng activities

# Batch size (tăng để nhanh hơn)
BATCH_SIZE = 5000  # Tăng từ 1000 → 5000

# Countries
COUNTRIES = ['VN', 'US']  # Chỉ 2 countries

# Activity types
ACTION_TYPES = ['LOGIN', 'VIEW']  # Chỉ 2 action types
```

### Parallel Data Generation

Để generate data nhanh hơn, có thể chạy parallel:

```bash
# Generate users only
python scripts/generate_dummy_data.py --users-only

# Generate projects only
python scripts/generate_dummy_data.py --projects-only

# (Cần modify script để support command line args)
```

## Summary

✅ **Script tạo 175,000+ rows realistic data**
✅ **pgAdmin4 GUI để browse data dễ dàng**
✅ **Ready để test cache, performance, pagination**
✅ **Tất cả data có relationships đúng (foreign keys)**
✅ **Realistic data với Faker (emails, names, IPs, user agents)**

🎉 **Enjoy testing với 20,000+ users!**
