# pgAdmin4 Setup Guide

## Truy cập pgAdmin4

pgAdmin4 đã được cấu hình sẵn trong Docker và đang chạy tại:

**URL**: http://localhost:5050

**Login Credentials**:
- Email: `admin@admin.com`
- Password: `admin`

## Kết nối PostgreSQL Database

### Bước 1: Đăng nhập pgAdmin4
1. Mở trình duyệt và truy cập: http://localhost:5050
2. Đăng nhập với:
   - Email: `admin@admin.com`
   - Password: `admin`

### Bước 2: Add PostgreSQL Server

1. Click chuột phải vào **Servers** → **Register** → **Server**

2. **Tab General**:
   - Name: `Local PostgreSQL` (hoặc tên bất kỳ)

3. **Tab Connection**:
   - Host: `postgres` (tên container, KHÔNG phải localhost)
   - Port: `5432`
   - Maintenance database: `user_service_db`
   - Username: `postgres`
   - Password: `password`
   - ☑️ Save password

4. Click **Save**

### Bước 3: Xem dữ liệu

Sau khi kết nối thành công:

1. Mở: **Servers** → **Local PostgreSQL** → **Databases** → **user_service_db** → **Schemas** → **public** → **Tables**

2. Bạn sẽ thấy 4 bảng:
   - `users` (20,000 rows)
   - `projects` (5,000 rows)
   - `user_activities` (99,306 rows)
   - `user_projects` (70,098 rows)

3. Để xem dữ liệu:
   - Click chuột phải vào table → **View/Edit Data** → **All Rows**

## Thống kê Database

**Tổng số rows**: ~194,404 rows

### Chi tiết:

| Bảng | Số rows | Mô tả |
|------|---------|-------|
| users | 20,000 | Thông tin user (email, password, bio, country) |
| projects | 5,000 | Danh sách projects |
| user_activities | 99,306 | Lịch sử hoạt động của users |
| user_projects | 70,098 | Quan hệ user-project (members) |

### User Statistics:
- Active users: ~75%
- Superusers: ~20%
- Countries: VN, US, JP, KR, FR, GB, DE, CN, IN, BR, AU, CA, TH, SG, MY

### Project Statistics:
- Active projects: ~50%
- Status: planning, in_progress, completed, on_hold, cancelled

## Queries hữu ích

### 1. Xem 10 users mới nhất
```sql
SELECT id, email, full_name, country, created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;
```

### 2. Đếm users theo country
```sql
SELECT country, COUNT(*) as total
FROM users
GROUP BY country
ORDER BY total DESC;
```

### 3. Xem projects với số lượng members
```sql
SELECT p.name, COUNT(up.user_id) as members_count
FROM projects p
LEFT JOIN user_projects up ON p.id = up.project_id
GROUP BY p.id, p.name
ORDER BY members_count DESC
LIMIT 10;
```

### 4. Xem activities gần nhất
```sql
SELECT u.email, ua.action_type, ua.description, ua.created_at
FROM user_activities ua
JOIN users u ON ua.user_id = u.id
ORDER BY ua.created_at DESC
LIMIT 20;
```

### 5. Test login với user bất kỳ
```sql
SELECT email, hashed_password, is_active
FROM users
WHERE is_active = true
LIMIT 1;
```

**Note**: Password cho tất cả test users là: `password123`

## Troubleshooting

### Không connect được database?

1. **Kiểm tra containers đang chạy**:
   ```bash
   docker ps
   ```
   Đảm bảo có 3 containers: postgres, pgadmin, redis

2. **Restart containers**:
   ```bash
   docker-compose restart
   ```

3. **Kiểm tra logs**:
   ```bash
   docker logs user_service_postgres
   docker logs user_service_pgadmin
   ```

### pgAdmin không load được?

1. Clear browser cache
2. Thử trình duyệt khác
3. Restart pgAdmin container:
   ```bash
   docker-compose restart pgadmin
   ```

## Lệnh Docker hữu ích

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart pgadmin
docker-compose restart postgres

# Access PostgreSQL CLI directly
docker exec -it user_service_postgres psql -U postgres -d user_service_db
```

## Test Login với dummy user

Bạn có thể test login API với bất kỳ user nào trong database:

```bash
# Example user email (random)
Email: <any email from database>
Password: password123
```

Tất cả 20,000 users đều có password: `password123`
