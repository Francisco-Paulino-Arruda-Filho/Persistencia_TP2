from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.Employee import Employee

class Payroll(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    gross_salary: float
    deductions: float
    net_salary: float
    reference_month: str  # e.g.: "2025-03"

    employee: Optional[Employee] = Relationship(back_populates="payrolls")