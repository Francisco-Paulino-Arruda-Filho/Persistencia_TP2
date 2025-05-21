from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from app.models.Employee import Employee
from app.models.Benefit import Benefit

class EmployeeBenefit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    benefit_id: int = Field(foreign_key="benefit.id")
    start_date: str  
    end_date: Optional[str] = None
    custom_amount: Optional[float] = None

    employee: Optional[Employee] = Relationship(back_populates="benefits")
    benefit: Optional[Benefit] = Relationship(back_populates="employees")