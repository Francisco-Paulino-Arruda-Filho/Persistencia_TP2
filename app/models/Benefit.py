from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship

from app.models.EmployeeBenefit import EmployeeBenefit

class Benefit(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    amount: float
    type: str  # e.g.: "Transportation", "Food", etc.
    active: bool = True

    employees: List["EmployeeBenefit"] = Relationship(back_populates="benefit")