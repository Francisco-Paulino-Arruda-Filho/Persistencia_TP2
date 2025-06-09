from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

from app.models.Employee import EmployeeRead

if TYPE_CHECKING:
    from app.models.Employee import Employee

class DepartmentBase(SQLModel):
    name: str
    location: str
    description: Optional[str] = None
    extension: Optional[str] = None

class Department(DepartmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    manager_id: Optional[int] = Field(default=None, foreign_key="employee.id")
    
    # Especificar explicitamente a chave estrangeira para o gerente
    manager: Optional["Employee"] = Relationship(
        back_populates="managed_department",
        sa_relationship_kwargs={
            "uselist": False,
            "foreign_keys": "Department.manager_id"
        }
    )
    
    # Especificar explicitamente a chave estrangeira para os funcionários
    employees: List["Employee"] = Relationship(
        back_populates="department",
        sa_relationship_kwargs={"foreign_keys": "Employee.department_id"}
    )

class DepartmentCreate(DepartmentBase):
    manager_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None

class DepartmentRead(DepartmentBase):
    id: int
    manager: Optional[EmployeeRead] = None
    employees: List[EmployeeRead] = []

class DepartmentUpdate(SQLModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    extension: Optional[str] = None
    manager_id: Optional[int] = Field(default=None, nullable=True)  
    employee_ids: Optional[List[int]] = None