# models/Department.py
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Employee import Employee

class DepartmentBase(SQLModel):
    name: str
    location: str
    description: Optional[str] = None
    extension: Optional[str] = None

class Department(DepartmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    manager: Optional["Employee"] = Relationship(back_populates="managed_department", sa_relationship_kwargs={"uselist": False})
    employees: List["Employee"] = Relationship(back_populates="department")

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentRead(DepartmentBase):
    id: int

class DepartmentUpdate(SQLModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    extension: Optional[str] = None

"""
# models/Department.py
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Employee import Employee

class DepartmentBase(SQLModel):
    name: str
    location: str
    description: Optional[str] = None
    extension: Optional[str] = None

class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    manager_id: Optional[int] = Field(default=None, foreign_key="employee.id")

    manager: Optional["Employee"] = Relationship(
        back_populates="manages_department",
        sa_relationship_kwargs={"foreign_keys": "[Department.manager_id]"}
    )

class DepartmentRead(DepartmentBase):
    id: int

class DepartmentCreate(DepartmentBase):
    manager_id: Optional[int] = None
    employee_ids: Optional[List[int]] = []  # lista de IDs para associar

class DepartmentUpdate(SQLModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    extension: Optional[str] = None
    manager_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None


"""
