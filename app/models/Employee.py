from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.Department import Department
from app.models.EmployeeBenefit import EmployeeBenefit
from app.models.Payroll import Payroll

class Employee(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    cpf: str
    position: str
    admission_date: str  # you can use datetime.date if desired
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")

    department: Optional[Department] = Relationship(back_populates="employees")
    managed_department: Optional[Department] = Relationship(back_populates="manager", sa_relationship_kwargs={"uselist": False})

    payrolls: List["Payroll"] = Relationship(back_populates="employee")
    benefits: List["EmployeeBenefit"] = Relationship(back_populates="employee")