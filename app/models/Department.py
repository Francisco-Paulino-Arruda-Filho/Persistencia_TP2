from typing import List, Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.Employee import Employee

class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    location: str
    description: Optional[str] = None
    extension: Optional[str] = None

    manager: Optional["Employee"] = Relationship(back_populates="managed_department", sa_relationship_kwargs={"uselist": False})
    employees: List["Employee"] = Relationship(back_populates="department")
