from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Department import Department
    from app.models.EmployeeBenefit import EmployeeBenefit
    from app.models.Payroll import Payroll

    
class EmployeeBase(SQLModel):
    name: str
    cpf: str
    position: str
    admission_date: str  
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")

class Employee(EmployeeBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    department: Optional["Department"] = Relationship(back_populates="employees")
    managed_department: Optional["Department"] = Relationship(back_populates="manager", sa_relationship_kwargs={"uselist": False})

    payrolls: List["Payroll"] = Relationship(back_populates="employee")
    benefits: List["EmployeeBenefit"] = Relationship(back_populates="employee")

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeRead(EmployeeBase):
    id: int

class EmployeeUpdate(SQLModel):
    name: Optional[str] = None
    cpf: Optional[str] = None
    position: Optional[str] = None
    admission_date: Optional[str] = None
    department_id: Optional[int] = None