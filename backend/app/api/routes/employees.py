"""Employee management routes."""

from fastapi import APIRouter, Body, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession, RequireAdmin
from app.models.enums import UserRole
from app.schemas.employee import EmployeeAdminUpdate, EmployeeCreate, EmployeeResponse, EmployeeSelfUpdate, PaginatedEmployees
from app.services import employee_service
from app.services.mappers import employee_to_response

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=PaginatedEmployees)
def list_employees(
    db: DBSession,
    _: RequireAdmin,
    search: str | None = None,
    department: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = employee_service.list_employees(db, search=search, department=department, page=page, page_size=page_size)
    return PaginatedEmployees(
        items=[employee_to_response(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EmployeeResponse, status_code=201)
def create_employee(payload: EmployeeCreate, db: DBSession, admin: RequireAdmin):
    profile = employee_service.create_employee(db, payload, admin)
    return employee_to_response(profile)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str, db: DBSession, current_user: CurrentUser):
    profile = employee_service.get_employee(db, employee_id)
    if current_user.role == UserRole.EMPLOYEE and profile.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return employee_to_response(profile)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: str,
    db: DBSession,
    current_user: CurrentUser,
    body: dict = Body(...),
):
    profile = employee_service.get_employee(db, employee_id)
    if current_user.role == UserRole.ADMIN:
        payload = EmployeeAdminUpdate(**body)
        updated = employee_service.update_employee_admin(db, profile, payload, current_user)
    elif profile.user_id == current_user.id:
        allowed = {k: v for k, v in body.items() if k in EmployeeSelfUpdate.model_fields}
        payload = EmployeeSelfUpdate(**allowed)
        updated = employee_service.update_employee_self(db, profile, payload, current_user)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return employee_to_response(updated)


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: str, db: DBSession, admin: RequireAdmin):
    profile = employee_service.get_employee(db, employee_id)
    employee_service.delete_employee(db, profile, admin)
