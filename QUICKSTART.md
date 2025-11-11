# ⚡ QUICKSTART - 5 PHÚT CHẠY PROJECT

Hướng dẫn nhanh nhất để chạy project và test API.

---

## 1️⃣ SETUP DATABASE (2 phút)

### Option A: Docker (Đơn giản nhất - Khuyên dùng)

```bash
# Start PostgreSQL
docker-compose up -d

# Check
docker ps
```

✅ Database đã sẵn sàng tại `localhost:5432`

### Option B: Local PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Create database
psql postgres
CREATE DATABASE user_service_db;
\q
```

---

## 2️⃣ SETUP PYTHON (1 phút)

```bash
# Tạo virtual environment
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate  # Windows

# Install packages
pip install -r requirements.txt
```

---

## 3️⃣ RUN SERVER (30 giây)

```bash
uvicorn app.main:app --reload
```

Mở browser: **http://localhost:8000/docs** 🎉

---

## 4️⃣ TEST API (1 phút)

### Cách 1: Swagger UI (Interactive)

1. Mở: http://localhost:8000/docs
2. Test endpoint `/api/v1/auth/register`
3. Test endpoint `/api/v1/auth/login`
4. Copy token
5. Click "Authorize" button, paste token
6. Test các endpoints khác

### Cách 2: Python Script

```bash
python test_api.py
```

### Cách 3: cURL

```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "full_name": "Test User", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# Copy token từ response, thay YOUR_TOKEN

# Get current user
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 NHANH NHẤT: ONE-LINER

```bash
# Clone/CD vào project, sau đó:
docker-compose up -d && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload
```

Mở http://localhost:8000/docs và bắt đầu test! 🚀

---

## 📚 NEXT STEPS

1. Đọc [README.md](README.md) - Giải thích chi tiết các khái niệm
2. Đọc [LEARNING_PATH.md](LEARNING_PATH.md) - Lộ trình học từng bước
3. Explore code trong `app/` folder
4. Modify và thêm features mới

---

## 🐛 TROUBLESHOOTING

**Server không start:**
```bash
# Check port 8000 có bị chiếm không
lsof -i :8000
# Kill process nếu cần
kill -9 <PID>
```

**Database connection failed:**
```bash
# Check PostgreSQL đang chạy
docker ps  # nếu dùng docker
# hoặc
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

**Module not found:**
```bash
# Đảm bảo đang trong virtual environment
which python  # phải trỏ vào venv

# Reinstall
pip install -r requirements.txt
```

---

## ✨ CÁC ENDPOINTS QUAN TRỌNG

| Endpoint | Mô tả |
|----------|-------|
| `/docs` | Swagger UI - Interactive docs |
| `/redoc` | ReDoc - Alternative docs |
| `/health` | Health check |
| `/api/v1/auth/register` | Đăng ký user |
| `/api/v1/auth/login` | Login lấy token |
| `/api/v1/auth/me` | Thông tin user hiện tại |
| `/api/v1/users` | List users |
| `/api/v1/users/today` | Users đăng ký hôm nay |
| `/api/v1/users/{id}/activities` | Lịch sử hoạt động |
| `/api/v1/users/{id}/statistics` | User statistics |

Happy Coding! 🎉
