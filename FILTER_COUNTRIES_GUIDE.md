# Hướng Dẫn Sử Dụng Filter Countries

## Tính Năng Mới
Filter users theo nhiều quốc gia (multiple countries) với khả năng chọn multiple choice.

## API Endpoint
```
GET /api/v1/users/
```

## Query Parameters
- `skip`: Số record bỏ qua (pagination) - mặc định: 0
- `limit`: Số record tối đa trả về - mặc định: 100, max: 100
- `countries`: Filter theo nhiều quốc gia (multiple choice) - tùy chọn

## Cách Sử Dụng

### 1. Lấy tất cả users (không filter)
```bash
GET /api/v1/users?skip=0&limit=10
```

### 2. Filter theo 1 quốc gia
```bash
GET /api/v1/users?countries=VN
```

### 3. Filter theo nhiều quốc gia (Multiple Choice)
```bash
GET /api/v1/users?countries=VN&countries=US&countries=TH
```

## Ví Dụ Với cURL

### Test với 1 quốc gia
```bash
curl -X GET "http://localhost:8000/api/v1/users?countries=VN" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test với nhiều quốc gia
```bash
curl -X GET "http://localhost:8000/api/v1/users?countries=VN&countries=US&countries=TH" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test với pagination và filter
```bash
curl -X GET "http://localhost:8000/api/v1/users?countries=VN&countries=US&skip=0&limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Ví Dụ Với JavaScript/TypeScript

### Fetch API
```javascript
// Filter theo nhiều quốc gia
const countries = ['VN', 'US', 'TH'];
const params = new URLSearchParams();
countries.forEach(country => params.append('countries', country));
params.append('skip', '0');
params.append('limit', '10');

const response = await fetch(`http://localhost:8000/api/v1/users?${params}`, {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const users = await response.json();
```

### Axios
```javascript
import axios from 'axios';

const response = await axios.get('http://localhost:8000/api/v1/users', {
  params: {
    countries: ['VN', 'US', 'TH'],
    skip: 0,
    limit: 10
  },
  headers: {
    'Authorization': `Bearer ${accessToken}`
  },
  paramsSerializer: params => {
    // Serialize array parameters correctly
    return new URLSearchParams(
      Object.entries(params).flatMap(([key, val]) =>
        Array.isArray(val) ? val.map(v => [key, v]) : [[key, val]]
      )
    ).toString();
  }
});

const users = response.data;
```

## Ví Dụ Với Python

### Requests
```python
import requests

# Filter theo nhiều quốc gia
url = "http://localhost:8000/api/v1/users"
headers = {"Authorization": f"Bearer {access_token}"}
params = {
    "countries": ["VN", "US", "TH"],
    "skip": 0,
    "limit": 10
}

response = requests.get(url, headers=headers, params=params)
users = response.json()
```

## Response Example
```json
[
  {
    "id": 1,
    "email": "user1@example.com",
    "full_name": "Nguyen Van A",
    "country": "VN",
    "bio": "...",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  {
    "id": 2,
    "email": "user2@example.com",
    "full_name": "John Doe",
    "country": "US",
    "bio": "...",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-02T00:00:00Z",
    "updated_at": "2024-01-02T00:00:00Z"
  }
]
```

## Test Trên Swagger UI

1. Chạy server: `uvicorn app.main:app --reload`
2. Mở browser: `http://localhost:8000/docs`
3. Tìm endpoint `GET /api/v1/users/`
4. Click "Try it out"
5. Nhập values:
   - countries: Nhập từng quốc gia và click "Add string item" cho mỗi quốc gia
   - Ví dụ: Add "VN", Add "US", Add "TH"
6. Click "Execute"

## Implementation Details

### Files Modified
1. **app/crud/user.py**: Thêm function `get_multi_by_countries()`
   - Filter users theo list countries sử dụng SQLAlchemy `.in_()` operator
   - Support pagination với skip/limit

2. **app/api/endpoints/users.py**: Update endpoint `GET /users/`
   - Thêm parameter `countries: Optional[List[str]]`
   - Logic: nếu có countries thì filter, nếu không thì lấy tất cả

### SQL Query Example
```sql
-- Khi filter với countries=['VN', 'US', 'TH']
SELECT * FROM users
WHERE country IN ('VN', 'US', 'TH')
LIMIT 10 OFFSET 0;
```

## Use Cases
- Admin panel: Xem users từ các quốc gia cụ thể
- Analytics: Phân tích users theo vùng địa lý
- Client filter: Multiple choice countries filter
- Reports: Báo cáo users theo regions

## Notes
- Country codes sử dụng ISO 3166-1 alpha-2 format (VN, US, TH, JP,...)
- Filter là case-sensitive
- Nếu không truyền `countries`, API sẽ trả về tất cả users
- Maximum limit per request: 100 users
