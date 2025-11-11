"""
Project Management Endpoints

USE CASES:
- CRUD projects
- Add/Remove members
- Get project members list
- Get user's projects
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import project as crud_project
from app.schemas.project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectWithMembers,
    ProjectMemberAdd,
    ProjectMemberRemove
)
from app.models.user import User as UserModel
from app.api.dependencies import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Project])
def read_projects(
    skip: int = Query(0, ge=0, description="Số record bỏ qua (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Số record tối đa trả về"),
    status: str = Query(None, description="Filter theo status (planning, in_progress, completed,...)"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get danh sách projects với pagination và filter

    VÍ DỤ REQUEST:
    1. Tất cả projects:
       GET /api/v1/projects?skip=0&limit=10

    2. Filter theo status:
       GET /api/v1/projects?status=in_progress

    RESPONSE: List projects

    USE CASE:
    - Admin panel: Xem tất cả projects
    - Dashboard: List projects
    - Filter projects theo status
    """
    if status:
        projects = crud_project.get_projects_by_status(db, status=status, skip=skip, limit=limit)
    else:
        projects = crud_project.get_multi(db, skip=skip, limit=limit)
    return projects


@router.get("/my-projects", response_model=List[Project])
def read_my_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get danh sách projects mà current user tham gia

    VÍ DỤ REQUEST:
    GET /api/v1/projects/my-projects

    RESPONSE: List projects của user hiện tại

    USE CASE:
    - User dashboard: "My Projects"
    - User xem các project mình tham gia
    """
    projects = crud_project.get_projects_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return projects


@router.post("/", response_model=Project)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Tạo project mới

    VÍ DỤ REQUEST:
    POST /api/v1/projects
    {
        "name": "Website Redesign",
        "description": "Redesign company website",
        "status": "planning",
        "start_date": "2024-01-01T00:00:00Z"
    }

    RESPONSE: Project object mới tạo

    USE CASE:
    - User tạo project mới
    - Admin tạo project cho team

    LƯU Ý: Current user sẽ tự động là owner của project
    """
    # Check project name đã tồn tại chưa
    existing_project = crud_project.get_by_name(db, name=project_in.name)
    if existing_project:
        raise HTTPException(status_code=400, detail="Project name already exists")

    # Create project với current user làm owner
    project = crud_project.create(db, obj_in=project_in, owner_id=current_user.id)
    return project


@router.get("/{project_id}", response_model=ProjectWithMembers)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get project by ID (include members list)

    VÍ DỤ REQUEST:
    GET /api/v1/projects/1

    RESPONSE: Project info với danh sách members

    USE CASE:
    - View project details
    - Xem team members của project
    """
    project = crud_project.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check user có phải member của project không (nếu không phải admin)
    if not current_user.is_superuser:
        if not crud_project.is_member(db, project_id=project_id, user_id=current_user.id):
            raise HTTPException(status_code=403, detail="Not a member of this project")

    return project


@router.put("/{project_id}", response_model=Project)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update project

    VÍ DỤ REQUEST:
    PUT /api/v1/projects/1
    {
        "name": "Website Redesign v2",
        "status": "in_progress"
    }

    AUTHORIZATION:
    - Chỉ owner/admin của project hoặc superuser mới được update

    USE CASE:
    - Update project info
    - Change project status
    """
    # Check project exists
    project = crud_project.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permission: phải là member và có role owner/admin, hoặc là superuser
    if not current_user.is_superuser:
        member_role = crud_project.get_member_role(db, project_id=project_id, user_id=current_user.id)
        if member_role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check name không bị trùng (nếu update name)
    if project_in.name and project_in.name != project.name:
        existing_project = crud_project.get_by_name(db, name=project_in.name)
        if existing_project:
            raise HTTPException(status_code=400, detail="Project name already exists")

    # Update
    project = crud_project.update(db, db_obj=project, obj_in=project_in)
    return project


@router.delete("/{project_id}", response_model=Project)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete project

    VÍ DỤ REQUEST:
    DELETE /api/v1/projects/1

    AUTHORIZATION:
    - Chỉ owner của project hoặc superuser mới được delete

    USE CASE:
    - Admin xóa project
    - Owner cancel project

    LƯU Ý: Cascade delete - tất cả entries trong user_projects cũng bị xóa
    """
    # Check project exists
    project = crud_project.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permission: phải là owner hoặc superuser
    if not current_user.is_superuser:
        member_role = crud_project.get_member_role(db, project_id=project_id, user_id=current_user.id)
        if member_role != "owner":
            raise HTTPException(status_code=403, detail="Only project owner can delete project")

    # Delete
    project = crud_project.delete(db, project_id=project_id)
    return project


@router.post("/{project_id}/members", response_model=dict)
def add_project_member(
    project_id: int,
    member_in: ProjectMemberAdd,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Thêm member vào project

    VÍ DỤ REQUEST:
    POST /api/v1/projects/1/members
    {
        "user_id": 2,
        "role": "member"
    }

    AUTHORIZATION:
    - Chỉ owner/admin của project hoặc superuser mới được add member

    USE CASE:
    - Thêm team member vào project
    - Assign user to project
    """
    # Check project exists
    project = crud_project.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permission
    if not current_user.is_superuser:
        member_role = crud_project.get_member_role(db, project_id=project_id, user_id=current_user.id)
        if member_role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Add member
    success = crud_project.add_member(
        db,
        project_id=project_id,
        user_id=member_in.user_id,
        role=member_in.role
    )

    if not success:
        raise HTTPException(status_code=400, detail="User is already a member of this project")

    return {"message": "Member added successfully"}


@router.delete("/{project_id}/members", response_model=dict)
def remove_project_member(
    project_id: int,
    member_in: ProjectMemberRemove,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Xóa member khỏi project

    VÍ DỤ REQUEST:
    DELETE /api/v1/projects/1/members
    {
        "user_id": 2
    }

    AUTHORIZATION:
    - Chỉ owner/admin của project hoặc superuser mới được remove member
    - Không thể remove owner

    USE CASE:
    - Remove team member khỏi project
    - Unassign user from project
    """
    # Check project exists
    project = crud_project.get_by_id(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check permission
    if not current_user.is_superuser:
        member_role = crud_project.get_member_role(db, project_id=project_id, user_id=current_user.id)
        if member_role not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not enough permissions")

    # Check không thể remove owner
    target_role = crud_project.get_member_role(db, project_id=project_id, user_id=member_in.user_id)
    if target_role == "owner":
        raise HTTPException(status_code=400, detail="Cannot remove project owner")

    # Remove member
    success = crud_project.remove_member(
        db,
        project_id=project_id,
        user_id=member_in.user_id
    )

    if not success:
        raise HTTPException(status_code=400, detail="User is not a member of this project")

    return {"message": "Member removed successfully"}
