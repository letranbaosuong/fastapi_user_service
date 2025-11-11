"""
Project CRUD Operations

KHÁI NIỆM CRUD:
- Create: Tạo project mới
- Read: Đọc thông tin project
- Update: Cập nhật thông tin
- Delete: Xóa project
- Add/Remove Members: Quản lý members trong project

VÍ DỤ:
crud.project.create(db, obj_in=project_data)
=> INSERT INTO projects ...
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.project import Project, user_projects
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_by_id(db: Session, project_id: int) -> Optional[Project]:
    """
    Lấy project theo ID

    VÍ DỤ:
    project = get_by_id(db, 1)
    => SELECT * FROM projects WHERE id = 1
    """
    return db.query(Project).filter(Project.id == project_id).first()


def get_by_name(db: Session, name: str) -> Optional[Project]:
    """
    Lấy project theo tên

    VÍ DỤ:
    project = get_by_name(db, "Website Redesign")
    => SELECT * FROM projects WHERE name = 'Website Redesign'
    """
    return db.query(Project).filter(Project.name == name).first()


def get_multi(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """
    Lấy danh sách projects với pagination

    VÍ DỤ:
    projects = get_multi(db, skip=0, limit=10)
    => SELECT * FROM projects LIMIT 10 OFFSET 0

    USE CASE: List projects trong admin panel
    - Page 1: skip=0, limit=10
    - Page 2: skip=10, limit=10
    """
    return db.query(Project).offset(skip).limit(limit).all()


def get_projects_by_status(
    db: Session,
    status: str,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """
    Lấy projects theo status

    VÍ DỤ:
    projects = get_projects_by_status(db, "in_progress")
    => SELECT * FROM projects WHERE status = 'in_progress'

    USE CASE:
    - Xem các project đang active
    - Filter projects theo trạng thái
    """
    return db.query(Project).filter(
        Project.status == status
    ).offset(skip).limit(limit).all()


def get_projects_by_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Project]:
    """
    Lấy tất cả projects mà user tham gia

    VÍ DỤ:
    projects = get_projects_by_user(db, user_id=1)
    => SELECT projects.* FROM projects
       JOIN user_projects ON projects.id = user_projects.project_id
       WHERE user_projects.user_id = 1

    USE CASE:
    - Xem danh sách projects của user
    - User dashboard
    """
    return db.query(Project).join(
        user_projects
    ).filter(
        user_projects.c.user_id == user_id
    ).offset(skip).limit(limit).all()


def create(db: Session, obj_in: ProjectCreate, owner_id: int) -> Project:
    """
    Tạo project mới và add owner vào project

    VÍ DỤ:
    project_data = ProjectCreate(
        name="Website Redesign",
        description="Redesign company website"
    )
    project = create(db, obj_in=project_data, owner_id=1)

    WORKFLOW:
    1. Create Project object
    2. Add to database
    3. Commit transaction
    4. Add owner vào project với role="owner"
    5. Refresh to get ID
    """
    db_obj = Project(
        name=obj_in.name,
        description=obj_in.description,
        status=obj_in.status or "planning",
        is_active=obj_in.is_active if obj_in.is_active is not None else True,
        start_date=obj_in.start_date,
        end_date=obj_in.end_date,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)

    # Add owner vào project
    owner = db.query(User).filter(User.id == owner_id).first()
    if owner:
        add_member(db, project_id=db_obj.id, user_id=owner_id, role="owner")

    return db_obj


def update(
    db: Session,
    db_obj: Project,
    obj_in: ProjectUpdate
) -> Project:
    """
    Update project

    VÍ DỤ:
    project = get_by_id(db, 1)
    update_data = ProjectUpdate(name="Website Redesign v2", status="in_progress")
    updated_project = update(db, db_obj=project, obj_in=update_data)

    WORKFLOW:
    1. Chỉ update fields có giá trị (không None)
    2. Commit changes
    3. Return updated object
    """
    update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete(db: Session, project_id: int) -> Optional[Project]:
    """
    Xóa project

    VÍ DỤ:
    deleted_project = delete(db, project_id=1)
    => DELETE FROM projects WHERE id = 1

    LƯU Ý: Cascade delete - tất cả entries trong user_projects cũng bị xóa
    """
    db_obj = get_by_id(db, project_id)
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


def add_member(
    db: Session,
    project_id: int,
    user_id: int,
    role: str = "member"
) -> bool:
    """
    Thêm user vào project

    VÍ DỤ:
    success = add_member(db, project_id=1, user_id=2, role="member")
    => INSERT INTO user_projects (project_id, user_id, role)
       VALUES (1, 2, 'member')

    USE CASE:
    - Thêm member mới vào project
    - Assign user to project

    RETURN: True nếu thành công, False nếu user đã tồn tại trong project
    """
    # Check xem user đã là member chưa
    existing = db.execute(
        user_projects.select().where(
            and_(
                user_projects.c.project_id == project_id,
                user_projects.c.user_id == user_id
            )
        )
    ).first()

    if existing:
        return False  # User đã là member rồi

    # Add user vào project
    db.execute(
        user_projects.insert().values(
            project_id=project_id,
            user_id=user_id,
            role=role
        )
    )
    db.commit()
    return True


def remove_member(
    db: Session,
    project_id: int,
    user_id: int
) -> bool:
    """
    Xóa user khỏi project

    VÍ DỤ:
    success = remove_member(db, project_id=1, user_id=2)
    => DELETE FROM user_projects
       WHERE project_id = 1 AND user_id = 2

    USE CASE:
    - Remove member khỏi project
    - Unassign user from project

    RETURN: True nếu thành công, False nếu user không phải member
    """
    # Check xem user có phải member không
    existing = db.execute(
        user_projects.select().where(
            and_(
                user_projects.c.project_id == project_id,
                user_projects.c.user_id == user_id
            )
        )
    ).first()

    if not existing:
        return False  # User không phải member

    # Remove user khỏi project
    db.execute(
        user_projects.delete().where(
            and_(
                user_projects.c.project_id == project_id,
                user_projects.c.user_id == user_id
            )
        )
    )
    db.commit()
    return True


def get_members(db: Session, project_id: int) -> List[User]:
    """
    Lấy danh sách members của project

    VÍ DỤ:
    members = get_members(db, project_id=1)
    => SELECT users.* FROM users
       JOIN user_projects ON users.id = user_projects.user_id
       WHERE user_projects.project_id = 1

    USE CASE:
    - Xem ai đang tham gia project
    - List team members
    """
    return db.query(User).join(
        user_projects
    ).filter(
        user_projects.c.project_id == project_id
    ).all()


def is_member(db: Session, project_id: int, user_id: int) -> bool:
    """
    Check xem user có phải member của project không

    VÍ DỤ:
    is_member = is_member(db, project_id=1, user_id=2)
    => SELECT * FROM user_projects
       WHERE project_id = 1 AND user_id = 2

    USE CASE:
    - Authorization: Check quyền truy cập project
    - Validate user có quyền edit project không
    """
    result = db.execute(
        user_projects.select().where(
            and_(
                user_projects.c.project_id == project_id,
                user_projects.c.user_id == user_id
            )
        )
    ).first()

    return result is not None


def get_member_role(db: Session, project_id: int, user_id: int) -> Optional[str]:
    """
    Lấy role của user trong project

    VÍ DỤ:
    role = get_member_role(db, project_id=1, user_id=2)
    => Return: "owner" hoặc "admin" hoặc "member" hoặc None

    USE CASE:
    - Authorization: Check role để xác định permissions
    - Show role badge trong UI
    """
    result = db.execute(
        user_projects.select().where(
            and_(
                user_projects.c.project_id == project_id,
                user_projects.c.user_id == user_id
            )
        )
    ).first()

    return result.role if result else None
