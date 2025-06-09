from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Employee import Employee
    from app.models.Benefit import Benefit

class EmployeeBenefitBase(SQLModel):
    start_date: str
    end_date: str
    custom_amount: float
    employee_id: int = Field(foreign_key="employee.id")
    benefit_id: int = Field(foreign_key="benefit.id")

class EmployeeBenefit(EmployeeBenefitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    employee: Optional["Employee"] = Relationship(back_populates="benefits")
    benefit: Optional["Benefit"] = Relationship(back_populates="employees")

class EmployeeBenefitCreate(EmployeeBenefitBase):
    employee_id: int
    benefit_id: int

class EmployeeBenefitRead(EmployeeBenefitBase):
    id: int

class EmployeeBenefitUpdate(EmployeeBenefitBase):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    custom_amount: Optional[float] = None
