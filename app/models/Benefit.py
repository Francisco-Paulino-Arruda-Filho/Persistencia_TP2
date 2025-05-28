from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.EmployeeBenefit import EmployeeBenefit

class BenefitBase(SQLModel):
    name: str
    description: Optional[str] = None
    amount: float
    type: str
    active: bool = True

class Benefit(BenefitBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employees: List["EmployeeBenefit"] = Relationship(back_populates="benefit")

class BenefitCreate(BenefitBase):
    pass

class BenefitRead(BenefitBase):
    id: int

class BenefitUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None
    active: Optional[bool] = None
