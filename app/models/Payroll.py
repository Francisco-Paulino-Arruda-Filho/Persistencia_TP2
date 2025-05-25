from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Employee import Employee

class Payroll(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    gross_salary: float
    deductions: float
    net_salary: float
    reference_month: str  

    employee: Optional["Employee"] = Relationship(back_populates="payrolls")
