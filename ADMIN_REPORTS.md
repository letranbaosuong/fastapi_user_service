# 📊 ADMIN REPORTS API

Tài liệu hướng dẫn sử dụng các API reports dành cho admin.

---

## 🎯 TỔNG QUAN

### Features đã implement:
✅ **User Statistics by Time Period**
- Số user mới hôm nay
- Số user mới hôm qua
- Số user mới 7 ngày gần đây
- Số user mới 30 ngày gần đây

✅ **Geographic Analytics**
- Thống kê user theo quốc gia
- Phân bố user toàn cầu
- Lọc user theo quốc gia cụ thể

✅ **Overall Dashboard Stats**
- Tổng số user
- User active/inactive
- Growth metrics
- Country diversity

✅ **Daily Statistics**
- Thống kê theo từng ngày
- User mới mỗi ngày
- Trend analysis

✅ **Dynamic Filtering (GraphQL-like)**
- Lọc theo country
- Lọc theo is_active
- Lọc theo is_superuser
- Lọc theo thời gian đăng ký
- Combine multiple filters

---

## 🔐 AUTHENTICATION

**CHỈ ADMIN** (user có `is_superuser=true`) mới có quyền truy cập các endpoints này.

### Cách set user thành admin:

**Option 1: Qua SQL**
```sql
UPDATE users SET is_superuser = true WHERE email = 'your@email.com';
```

**Option 2: Qua script**
```bash
python create_admin.py --email admin@admin.com --password admin123
```

### Cách login và lấy token:

**1. Login:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=suong@gmail.com&password=yourpassword"
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**2. Dùng token cho các request tiếp theo:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/admin/reports/stats/overall" \
  -H "Authorization: Bearer eyJhbGci..."
```

---

## 📍 API ENDPOINTS

### 1. Overall Statistics

**GET** `/api/v1/admin/reports/stats/overall`

Lấy tổng quan thống kê hệ thống.

**Response:**
```json
{
  "total_users": 10000,
  "active_users": 8000,
  "inactive_users": 2000,
  "new_today": 50,
  "new_yesterday": 45,
  "new_last_7_days": 300,
  "total_countries": 25
}
```

**Use Case:**
- Dashboard admin overview
- Quick health check
- KPI monitoring

---

### 2. New Users Statistics

**GET** `/api/v1/admin/reports/stats/new-users?period={period}`

Lấy số user mới theo khoảng thời gian.

**Parameters:**
- `period`: `today`, `yesterday`, `last_7_days`, `last_30_days`

**Example Request:**
```bash
GET /api/v1/admin/reports/stats/new-users?period=last_7_days
```

**Response:**
```json
{
  "total": 300,
  "period": "last_7_days",
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-01-07T23:59:59"
}
```

**Use Case:**
- Growth tracking
- Period comparison
- Marketing campaign effectiveness

---

### 3. Users by Country Statistics

**GET** `/api/v1/admin/reports/stats/by-country`

Lấy phân bố user theo quốc gia.

**Response:**
```json
[
  {
    "country": "VN",
    "total_users": 1500,
    "active_users": 1200,
    "percentage": 35.5
  },
  {
    "country": "US",
    "total_users": 800,
    "active_users": 700,
    "percentage": 18.9
  }
]
```

**Use Case:**
- Geographic analysis
- Market penetration
- Localization planning

---

### 4. Daily Statistics

**GET** `/api/v1/admin/reports/stats/daily?days={days}`

Lấy thống kê theo từng ngày.

**Parameters:**
- `days`: Số ngày (1-90, default: 7)

**Example Request:**
```bash
GET /api/v1/admin/reports/stats/daily?days=7
```

**Response:**
```json
[
  {
    "date": "2024-01-01",
    "new_users": 50,
    "active_users": 500,
    "total_users": 5000
  },
  {
    "date": "2024-01-02",
    "new_users": 45,
    "active_users": 520,
    "total_users": 5045
  }
]
```

**Use Case:**
- Chart visualization
- Trend analysis
- Daily performance

---

### 5. Dynamic Filtering (GraphQL-like)

**GET** `/api/v1/admin/reports/users/filter?{filters}`

Lọc user với nhiều điều kiện kết hợp.

**Parameters (tất cả optional):**
- `country`: Mã quốc gia (VN, US, JP, ...)
- `is_active`: true/false
- `is_superuser`: true/false
- `days`: Số ngày gần đây (user đăng ký trong N ngày)
- `skip`: Pagination offset (default: 0)
- `limit`: Max records (1-1000, default: 100)

**Example 1: User từ Vietnam**
```bash
GET /api/v1/admin/reports/users/filter?country=VN
```

**Example 2: Active users từ Vietnam**
```bash
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true
```

**Example 3: Admin users**
```bash
GET /api/v1/admin/reports/users/filter?is_superuser=true
```

**Example 4: User đăng ký trong 7 ngày từ US**
```bash
GET /api/v1/admin/reports/users/filter?country=US&days=7
```

**Example 5: Combine tất cả filters**
```bash
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true&days=7&limit=50
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "full_name": "User One",
    "country": "VN",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T10:00:00",
    ...
  }
]
```

**Use Case:**
- Advanced search
- User segmentation
- Export specific user groups
- Custom reports

---

### 6. Users by Specific Country

**GET** `/api/v1/admin/reports/users/country/{country}?skip={skip}&limit={limit}`

Lấy tất cả user từ một quốc gia cụ thể.

**Example Request:**
```bash
GET /api/v1/admin/reports/users/country/VN?skip=0&limit=50
```

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Nguyen Van A",
    "country": "VN",
    ...
  }
]
```

**Use Case:**
- Country-specific analysis
- Export users by country

---

## 🧪 TESTING VỚI SWAGGER UI

1. **Mở Swagger UI:**
   ```
   http://127.0.0.1:8000/docs
   ```

2. **Login để lấy token:**
   - Tìm endpoint `POST /api/v1/auth/login`
   - Click **Try it out**
   - Nhập credentials:
     ```
     username: suong@gmail.com
     password: yourpassword
     ```
   - Click **Execute**
   - Copy `access_token`

3. **Authorize:**
   - Click nút **Authorize** (icon ổ khóa) ở góc trên
   - Nhập: `Bearer {your_token}`
   - Click **Authorize**

4. **Test admin endpoints:**
   - Scroll xuống section **admin-reports**
   - Thử các endpoints:
     - `GET /api/v1/admin/reports/stats/overall`
     - `GET /api/v1/admin/reports/stats/new-users`
     - `GET /api/v1/admin/reports/stats/by-country`
     - `GET /api/v1/admin/reports/users/filter`

---

## 🔒 PHÂN QUYỀN

### User thường (is_superuser=false):
❌ Không thể truy cập `/api/v1/admin/reports/*`
✅ Chỉ xem được thông tin của chính mình

### Admin (is_superuser=true):
✅ Truy cập tất cả endpoints
✅ Xem thống kê toàn hệ thống
✅ Filter và export user data
✅ Analytics và reports

### Response khi không có quyền:
```json
{
  "detail": "The user doesn't have enough privileges"
}
```

---

## 💡 USE CASES THỰC TẾ

### 1. Dashboard Admin
```bash
# Lấy overview stats
GET /api/v1/admin/reports/stats/overall

# Lấy thống kê 7 ngày
GET /api/v1/admin/reports/stats/daily?days=7

# Lấy phân bố quốc gia
GET /api/v1/admin/reports/stats/by-country
```

### 2. Growth Analysis
```bash
# Compare hôm nay vs hôm qua
GET /api/v1/admin/reports/stats/new-users?period=today
GET /api/v1/admin/reports/stats/new-users?period=yesterday

# Trend 30 ngày
GET /api/v1/admin/reports/stats/daily?days=30
```

### 3. Geographic Analysis
```bash
# Tất cả quốc gia
GET /api/v1/admin/reports/stats/by-country

# Chi tiết user từ Vietnam
GET /api/v1/admin/reports/users/country/VN
```

### 4. User Segmentation
```bash
# Active users từ VN đăng ký trong 7 ngày
GET /api/v1/admin/reports/users/filter?country=VN&is_active=true&days=7

# Inactive users cần re-engage
GET /api/v1/admin/reports/users/filter?is_active=false&days=30

# New users cần onboarding
GET /api/v1/admin/reports/users/filter?days=7&is_active=true
```

---

## 🗄️ DATABASE SCHEMA

### User Model với Country:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    country VARCHAR(2),  -- ← NEW FIELD
    bio TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_users_country ON users(country);
```

### Migration:
```bash
# Chạy migration
docker exec user_service_postgres psql -U postgres -d user_service_db < migrations/add_country_column.sql
```

---

## 📝 NOTES

### Country Codes:
- Sử dụng **ISO 3166-1 alpha-2** (2 ký tự)
- Examples: VN, US, JP, KR, CN, TH, SG, etc.
- Nullable (user có thể không có country)

### Performance:
- Index trên `country` column để query nhanh
- Pagination với `skip` và `limit`
- Max limit: 1000 records/request

### Security:
- Tất cả endpoints require authentication
- Admin authorization check với `is_superuser`
- Token-based authentication (JWT)

---

## 🚀 NEXT STEPS

### Features có thể mở rộng:
1. **Export to CSV/Excel**
   - Export filtered users
   - Download reports

2. **Advanced Filters**
   - Date range picker
   - Multiple countries
   - Custom date ranges

3. **Charts & Visualization**
   - Integration với Chart.js
   - Real-time updates
   - Interactive dashboards

4. **Email Reports**
   - Schedule daily/weekly reports
   - Send via email
   - Custom templates

5. **Caching**
   - Cache expensive queries
   - Redis integration
   - Invalidation strategy

---

Chúc bạn sử dụng thành công! 🎉
