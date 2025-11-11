"""
API Router - Tổng hợp tất cả endpoints

KHÁI NIỆM:
- Include các sub-routers vào main API router
- Prefix để group các endpoints liên quan
"""

from fastapi import APIRouter
from app.api.endpoints import auth, users, activities, admin

api_router = APIRouter()

# Authentication routes
# VÍ DỤ: /api/v1/auth/login, /api/v1/auth/register
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# User routes
# VÍ DỤ: /api/v1/users, /api/v1/users/1
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Activity routes
# VÍ DỤ: /api/v1/users/1/activities
api_router.include_router(activities.router, prefix="/users", tags=["activities"])

# Admin routes - ADMIN ONLY
# VÍ DỤ: /api/v1/admin/reports/stats/overall, /api/v1/admin/reports/users/filter
api_router.include_router(admin.router, prefix="/admin/reports", tags=["admin-reports"])
