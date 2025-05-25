from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.EmployeeBenefit import EmployeeBenefit

class Benefit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    amount: float
    type: str  
    active: bool = True

    employees: List["EmployeeBenefit"] = Relationship(back_populates="benefit")
