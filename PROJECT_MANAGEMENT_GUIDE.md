# Hướng Dẫn Quản Lý Projects (Many-to-Many Relationship)

## Tổng Quan

Tính năng Project Management cho phép:
- Tạo và quản lý projects
- Mối quan hệ **nhiều-nhiều** (many-to-many) giữa Users và Projects
- 1 User có thể tham gia nhiều Projects
- 1 Project có thể có nhiều Users (members)
- Quản lý roles: owner, admin, member

## Database Structure

### Bảng Projects
```sql
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'planning',
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### Association Table (user_projects)
```sql
CREATE TABLE user_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'member',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Many-to-Many Relationship
```
User 1 ←→ Many Projects
Project 1 ←→ Many Users

Thông qua bảng user_projects (association table)
```

## API Endpoints

### 1. Get All Projects
```
GET /api/v1/projects
```

**Query Parameters:**
- `skip`: Pagination offset (default: 0)
- `limit`: Max records (default: 100)
- `status`: Filter by status (optional)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/projects?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
[
  {
    "id": 1,
    "name": "Website Redesign",
    "description": "Redesign company website",
    "status": "in_progress",
    "is_active": true,
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": null,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": null
  }
]
```

### 2. Get My Projects (Current User's Projects)
```
GET /api/v1/projects/my-projects
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/projects/my-projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Create Project
```
POST /api/v1/projects
```

**Request Body:**
```json
{
  "name": "Mobile App Development",
  "description": "Build iOS and Android app",
  "status": "planning",
  "start_date": "2024-02-01T00:00:00Z"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/projects" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App Development",
    "description": "Build iOS and Android app",
    "status": "planning"
  }'
```

**Response:** Project object (current user tự động là owner)

### 4. Get Project by ID (with Members)
```
GET /api/v1/projects/{project_id}
```

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/projects/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Example Response:**
```json
{
  "id": 1,
  "name": "Website Redesign",
  "description": "Redesign company website",
  "status": "in_progress",
  "is_active": true,
  "members": [
    {
      "id": 1,
      "email": "john@example.com",
      "full_name": "John Doe",
      "country": "US"
    },
    {
      "id": 2,
      "email": "alice@example.com",
      "full_name": "Alice Smith",
      "country": "VN"
    }
  ],
  "created_at": "2024-01-01T10:00:00Z"
}
```

### 5. Update Project
```
PUT /api/v1/projects/{project_id}
```

**Authorization:** Only owner/admin or superuser

**Request Body:**
```json
{
  "name": "Website Redesign v2",
  "status": "in_progress",
  "is_active": true
}
```

**Example Request:**
```bash
curl -X PUT "http://localhost:8000/api/v1/projects/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

### 6. Delete Project
```
DELETE /api/v1/projects/{project_id}
```

**Authorization:** Only owner or superuser

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/projects/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Add Member to Project
```
POST /api/v1/projects/{project_id}/members
```

**Authorization:** Only owner/admin or superuser

**Request Body:**
```json
{
  "user_id": 2,
  "role": "member"
}
```

**Roles:**
- `owner`: Full control (can delete project)
- `admin`: Can manage members and update project
- `member`: Can view and work on project

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/projects/1/members" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "role": "member"
  }'
```

**Response:**
```json
{
  "message": "Member added successfully"
}
```

### 8. Remove Member from Project
```
DELETE /api/v1/projects/{project_id}/members
```

**Authorization:** Only owner/admin or superuser

**Request Body:**
```json
{
  "user_id": 2
}
```

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/projects/1/members" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'
```

**Note:** Cannot remove owner

## JavaScript/TypeScript Examples

### Create Project
```javascript
const createProject = async (projectData) => {
  const response = await fetch('http://localhost:8000/api/v1/projects', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'Mobile App',
      description: 'Build iOS and Android app',
      status: 'planning'
    })
  });

  return await response.json();
};
```

### Add Member to Project
```javascript
const addMember = async (projectId, userId, role = 'member') => {
  const response = await fetch(
    `http://localhost:8000/api/v1/projects/${projectId}/members`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: userId,
        role: role
      })
    }
  );

  return await response.json();
};
```

### Get My Projects
```javascript
const getMyProjects = async () => {
  const response = await fetch(
    'http://localhost:8000/api/v1/projects/my-projects',
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );

  return await response.json();
};
```

## Python Examples

### Create Project
```python
import requests

def create_project(access_token, name, description):
    url = "http://localhost:8000/api/v1/projects"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "description": description,
        "status": "planning"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

### Add Member
```python
def add_member(access_token, project_id, user_id, role="member"):
    url = f"http://localhost:8000/api/v1/projects/{project_id}/members"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "user_id": user_id,
        "role": role
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

## Use Cases

### 1. Project Team Management
```
Scenario: Team lead tạo project và add members

1. Team lead tạo project
   POST /api/v1/projects
   => Team lead tự động là owner

2. Add developers vào team
   POST /api/v1/projects/1/members
   { "user_id": 2, "role": "member" }
   { "user_id": 3, "role": "member" }

3. Add project manager
   POST /api/v1/projects/1/members
   { "user_id": 4, "role": "admin" }
```

### 2. User Dashboard - My Projects
```
Scenario: User xem tất cả projects mình tham gia

GET /api/v1/projects/my-projects
=> Trả về list tất cả projects mà user là member
```

### 3. Project Access Control
```
Scenario: Check user có quyền access project không

1. Get project details
   GET /api/v1/projects/1

2. Nếu user không phải member
   => 403 Forbidden: "Not a member of this project"

3. Nếu user là member
   => Trả về project info với members list
```

## Testing on Swagger UI

1. Chạy server: `uvicorn app.main:app --reload`
2. Mở Swagger UI: `http://localhost:8000/docs`
3. Authenticate:
   - Expand `POST /api/v1/auth/login`
   - Login và copy access token
   - Click "Authorize" button ở top
   - Paste token: `Bearer YOUR_TOKEN`

4. Test endpoints:
   - Create project: `POST /api/v1/projects`
   - Add member: `POST /api/v1/projects/{project_id}/members`
   - Get my projects: `GET /api/v1/projects/my-projects`

## Database Migrations

Để tạo tables trong database:

```bash
# Nếu sử dụng Alembic
alembic revision --autogenerate -m "Add Project and user_projects tables"
alembic upgrade head

# Hoặc nếu dùng auto create từ SQLAlchemy
# Tables sẽ tự động được tạo khi start server
python app/main.py
```

## Files Created/Modified

### Models
- `app/models/project.py` - Project model và association table
- `app/models/user.py` - Thêm relationship với Project
- `app/models/__init__.py` - Import Project model

### Schemas
- `app/schemas/project.py` - Project validation schemas
- `app/schemas/__init__.py` - Export Project schemas

### CRUD
- `app/crud/project.py` - Project CRUD operations

### Endpoints
- `app/api/endpoints/projects.py` - Project API endpoints
- `app/api/api.py` - Include projects router

## Architecture Benefits

### Many-to-Many Relationship
- **Flexible:** User có thể tham gia nhiều projects
- **Scalable:** Project có thể có unlimited members
- **Maintainable:** Clear separation với association table

### Role-based Access
- **Security:** Check permissions trước khi action
- **Granular control:** owner > admin > member
- **Audit:** Track role trong user_projects table

### Clean Code
- **Reusable:** CRUD functions độc lập
- **Testable:** Easy to unit test
- **Documented:** Comprehensive Vietnamese comments
