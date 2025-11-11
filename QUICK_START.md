# Quick Start Guide

## ⚠️ QUAN TRỌNG: Virtual Environment

Project này dùng **venv** (virtual environment). Bạn cần install dependencies vào venv!

### Quick Fix (Nếu gặp lỗi "No module named 'faker'"):

```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install faker==22.0.0 tqdm==4.66.1

# Chạy script
python scripts/generate_dummy_data.py
```

---

## Generate Dummy Data - 3 Cách

### Cách 1: One-Click Script (Recommended) ⭐

```bash
# Từ project root
./scripts/setup_and_generate.sh
```

**Script sẽ tự động:**
1. Detect và activate venv (nếu có)
2. Check Python & Docker
3. Install dependencies vào venv
4. Start Docker services
5. Generate 175,000+ rows
6. Show statistics

**Time:** ~3-4 minutes (bao gồm cả install)

---

### Cách 2: Install Dependencies Script

```bash
# Tự động install vào venv hoặc global
./scripts/install_dependencies.sh

# Sau đó generate data
source venv/bin/activate  # Nếu dùng venv
python scripts/generate_dummy_data.py
```

---

### Cách 3: Manual (Step by Step)

```bash
# 1. Activate venv (QUAN TRỌNG!)
source venv/bin/activate

# 2. Install dependencies
pip install faker==22.0.0 tqdm==4.66.1

# 3. Start Docker services
docker-compose up -d

# 4. Wait for PostgreSQL ready (~10 seconds)
sleep 10

# 5. Generate data
python scripts/generate_dummy_data.py
```

**Time:** ~2-3 minutes

---

## Troubleshooting

### Error: "No module named 'faker'" ⚠️ PHỔ BIẾN

**Nguyên nhân:** Dependencies chưa được install vào venv

**Solution 1: Quick Fix (Recommended)**
```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install faker==22.0.0 tqdm==4.66.1

# Verify installation
pip list | grep faker
pip list | grep tqdm

# Run script
python scripts/generate_dummy_data.py
```

**Solution 2: Use Install Script**
```bash
./scripts/install_dependencies.sh
```

**Solution 3: Check Which Python You're Using**
```bash
# Inside venv
which python  # Should show: /path/to/project/venv/bin/python

# Outside venv
which python3  # Shows system Python

# Make sure you're in venv before installing!
```

---

### Error: "No such file or directory"

**Problem:** Script tìm không thấy file

**Solution:** Chạy từ project root
```bash
cd /path/to/fastapi_user_service
source venv/bin/activate
python scripts/generate_dummy_data.py
```

---

### Error: "could not connect to server"

**Solution:** Start PostgreSQL
```bash
docker-compose up -d postgres

# Wait for ready
sleep 10

# Check
docker exec user_service_postgres pg_isready -U postgres
```

---

## What Gets Generated?

```
✅ 20,000 users
   - Unique emails
   - Realistic names (multi-language)
   - 15 countries (VN, US, JP, ...)
   - 75% active users
   - 20% superusers

✅ 5,000 projects
   - Realistic names
   - 5 statuses (planning, in_progress, ...)
   - Start/end dates

✅ 100,000+ user activities
   - 8 action types (LOGIN, CREATE, ...)
   - IP addresses
   - User agents

✅ 50,000+ user-project memberships
   - 3 roles (owner, admin, member)
   - Random join dates

📊 TOTAL: ~175,000 rows
⏱️  TIME: 2-3 minutes
```

---

## After Generation

### 1. View in pgAdmin4

```bash
# Access
open http://localhost:5050

# Login
Email: admin@admin.com
Password: admin

# Connect to server
Host: postgres
Port: 5432
Database: user_service_db
Username: postgres
Password: password
```

### 2. Start API Server

```bash
# Start FastAPI
uvicorn app.main:app --reload

# Access Swagger UI
open http://localhost:8000/docs

# Test endpoints với 20,000 users!
```

### 3. Test Cache Performance

```bash
# First request (Cache MISS)
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
# ~150ms

# Second request (Cache HIT)
curl -X GET "http://localhost:8000/api/v1/users?skip=0&limit=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
# ~5ms (30x faster!)
```

---

## Clear Data

```bash
# Option 1: Re-run script với clear
python scripts/generate_dummy_data.py
# Chọn 'yes' khi hỏi clear data

# Option 2: SQL truncate
docker exec user_service_postgres psql -U postgres -d user_service_db <<EOF
TRUNCATE TABLE user_activities CASCADE;
TRUNCATE TABLE user_projects CASCADE;
TRUNCATE TABLE projects CASCADE;
TRUNCATE TABLE users CASCADE;
EOF
```

---

## Tips

💡 **Tăng tốc độ:** Edit `BATCH_SIZE` trong script (default: 1000)

💡 **Giảm data:** Edit `NUM_USERS`, `NUM_PROJECTS` trong script

💡 **Check progress:** Script có progress bars (tqdm)

💡 **View logs:** Mở terminal thứ 2 để xem Docker logs
```bash
docker-compose logs -f postgres
```

---

## Next Steps

1. ✅ Generate data
2. 📊 View in pgAdmin4
3. 🚀 Start API server
4. 🧪 Test endpoints
5. 🎯 Test cache performance
6. 📈 Run SQL queries

**Full Documentation:**
- `DUMMY_DATA_GUIDE.md` - Comprehensive guide
- `REDIS_CACHE_GUIDE.md` - Cache testing
- `PROJECT_MANAGEMENT_GUIDE.md` - API features

---

**🎉 Enjoy testing with 175,000+ rows!**
