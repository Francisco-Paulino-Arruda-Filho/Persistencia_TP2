from fastapi import APIRouter, Depends, HTTPException
from app.models import Employee
from app.models.Department import Department
from ..core.db import get_session

router = APIRouter(prefix="/employees", tags=["Funcionários"])

@router.get("/", response_model=list[Department])
def get_all_employees(session=Depends(get_session)):
    """
    Obtém todos os funcionários.
    """
    employees = session.query(Department).all()
    return employees

@router.post("/", response_model=Department)
def create_employee(employee: Department, session=Depends(get_session)):
    """
    Cria um novo funcionário.
    """
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee

def get_employee(employee_id: int, session=Depends(get_session)):
    """
    Obtém um funcionário pelo ID.
    """
    employee = session.query(Department).filter(Department.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee

@router.get("/{employee_id}", response_model=Department)
def read_employee(employee_id: int, session=Depends(get_session)):
    """
    Lê um funcionário pelo ID.
    """
    return get_employee(employee_id, session)

@router.put("/{employee_id}", response_model=Department)
def update_employee(employee_id: int, employee: Department, session=Depends(get_session)):
    """
    Atualiza um funcionário existente.
    """
    db_employee = get_employee(employee_id, session)
    for key, value in employee.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)
    session.commit()
    session.refresh(db_employee)
    return db_employee

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, session=Depends(get_session)):
    """
    Deleta um funcionário pelo ID.
    """
    employee = get_employee(employee_id, session)
    session.delete(employee)
    session.commit()
    return {"message": "Funcionário deletado com sucesso"}

@router.get("/search/{name}", response_model=list[Employee])
def search_employee_by_name(name: str, session=Depends(get_session)):
    """
    Busca funcionários pelo nome.
    """
    employees = session.query(Department).filter(Department.name.ilike(f"%{name}%")).all()
    if not employees:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/department/{department_id}", response_model=list[Department])
def get_employees_by_department(department_id: int, session=Depends(get_session)):
    """
    Obtém funcionários por departamento.
    """
    employees = session.query(Department).filter(Department.department_id == department_id).all()
    if not employees:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/position/{position}", response_model=list[Department])
def get_employees_by_position(position: str, session=Depends(get_session)):
    """
    Obtém funcionários por cargo.
    """
    employees = session.query(Department).filter(Department.position.ilike(f"%{position}%")).all()
    if not employees:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/search", response_model=list[Employee])
def search_employees(session=Depends(get_session), name: str = None, position: str = None):
    """
    Busca funcionários por nome ou cargo.
    """
    query = session.query(Department)
    if name:
        query = query.filter(Department.name.ilike(f"%{name}%"))
    if position:
        query = query.filter(Department.position.ilike(f"%{position}%"))
    
    employees = query.all()
    if not employees:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    return employees