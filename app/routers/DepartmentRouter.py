from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.Department import Department, DepartmentCreate, DepartmentRead, DepartmentUpdate
from ..core.db import get_session
from ..logs.logger import logger

router = APIRouter(prefix="/departments", tags=["Departamentos"])

@router.post("/", response_model=DepartmentRead)
def create_department(department: DepartmentCreate, session=Depends(get_session)):
    """
    Cria um novo departamento.
    """
    logger.debug(f"Tentando criar departamento: {department}")
    try:
        db_department = Department(**department.dict())  # Cria o objeto com os dados recebidos
        session.add(db_department)
        session.commit()
        session.refresh(db_department)
        logger.info(f"Departamento criado com sucesso: {db_department}")
        return db_department
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Erro ao criar departamento")
        raise HTTPException(status_code=500, detail="Erro interno ao criar departamento")

def get_department(department_id: int, session=Depends(get_session)):
    """
    Obtém um departamento pelo ID.
    """
    try:
        department = session.query(Department).filter(Department.id == department_id).first()
        if not department:
            logger.warning(f"Departamento com ID {department_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")
        logger.debug(f"Departamento recuperado com sucesso: {department}")
        return department
    except SQLAlchemyError as e:
        logger.exception("Erro ao buscar departamento por ID")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento")

@router.put("/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, department: DepartmentUpdate, session=Depends(get_session)):
    db_department = get_department(department_id, session)
    update_data = department.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_department, key, value)
    session.commit()
    session.refresh(db_department)
    return db_department

@router.delete("/{department_id}")
def delete_department(department_id: int, session=Depends(get_session)):
    """
    Deleta um departamento pelo ID.
    """
    logger.debug(f"Tentando deletar departamento com ID {department_id}")
    try:
        department = get_department(department_id, session)
        session.delete(department)
        session.commit()
        logger.info(f"Departamento deletado com sucesso: ID {department_id}")
        return {"message": "Departamento deletado com sucesso"}
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Erro ao deletar departamento")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar departamento")

@router.get("/", response_model=list[Department])
def get_all_departments(session=Depends(get_session)):
    """
    Obtém todos os departamentos.
    """
    logger.debug("Solicitação para listar todos os departamentos")
    try:
        departments = session.query(Department).all()
        logger.info(f"{len(departments)} departamentos encontrados.")
        return departments
    except SQLAlchemyError as e:
        logger.exception("Erro ao listar departamentos")
        raise HTTPException(status_code=500, detail="Erro interno ao listar departamentos")

@router.get("/name/{department_name}", response_model=Department)
def read_department_by_name(department_name: str, session=Depends(get_session)):
    """
    Lê um departamento pelo nome.
    """
    logger.debug(f"Buscando departamento com nome '{department_name}'")
    try:
        department = session.query(Department).filter(Department.name == department_name).first()
        if not department:
            logger.warning(f"Departamento com nome '{department_name}' não encontrado.")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")
        logger.info(f"Departamento encontrado por nome: {department}")
        return department
    except SQLAlchemyError as e:
        logger.exception("Erro ao buscar departamento por nome")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento por nome")
    

"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models.Department import Department, DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.models.Employee import Employee

router = APIRouter(prefix="/departments", tags=["Departments"])

# Create a department
@router.post("/", response_model=DepartmentRead, status_code=status.HTTP_201_CREATED)
def create_department(dept: DepartmentCreate, session: Session = Depends(get_session)):
    db_dept = Department(name=dept.name, manager_id=dept.manager_id)
    session.add(db_dept)
    session.commit()
    session.refresh(db_dept)

    # Se vier employee_ids, associa os employees ao departamento
    if dept.employee_ids:
        employees = session.exec(select(Employee).where(Employee.id.in_(dept.employee_ids))).all()
        for emp in employees:
            emp.department_id = db_dept.id  # assumindo que Employee tem campo department_id
        session.commit()

    return db_dept

# Read all departments
@router.get("/", response_model=List[DepartmentRead])
def read_departments(session: Session = Depends(get_session)):
    departments = session.exec(select(Department)).all()
    return departments

# Read a single department
@router.get("/{department_id}", response_model=DepartmentRead)
def read_department(department_id: int, session: Session = Depends(get_session)):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    return department

# Update a department
@router.put("/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, dept_update: DepartmentUpdate, session: Session = Depends(get_session)):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Atualiza os campos fornecidos
    update_data = dept_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key != "employee_ids":
            setattr(department, key, value)

    # Atualiza os employees associados, se informado
    if "employee_ids" in update_data:
        # Desassocia todos os employees do departamento atual
        employees_current = session.exec(select(Employee).where(Employee.department_id == department_id)).all()
        for emp in employees_current:
            emp.department_id = None

        # Associa os novos employees
        employees_new = session.exec(select(Employee).where(Employee.id.in_(update_data["employee_ids"]))).all()
        for emp in employees_new:
            emp.department_id = department_id

    session.add(department)
    session.commit()
    session.refresh(department)
    return department

# Delete a department
@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(department_id: int, session: Session = Depends(get_session)):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")

    # Opcional: desassocia os employees do departamento antes de apagar
    employees = session.exec(select(Employee).where(Employee.department_id == department_id)).all()
    for emp in employees:
        emp.department_id = None

    session.delete(department)
    session.commit()

"""
