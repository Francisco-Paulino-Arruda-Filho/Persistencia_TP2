from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from app.models.Employee import Employee, EmployeeCreate, EmployeeRead, EmployeeUpdate
from ..core.db import get_session
from ..logs.logger import logger

router = APIRouter(prefix="/employees", tags=["Funcionários"])

@router.get("/", response_model=List[EmployeeRead])
def get_all_employees(session: Session = Depends(get_session)):
    try:
        employees = session.query(Employee).all()
        logger.debug("Recuperando todos os funcionários.")
        return employees
    except SQLAlchemyError:
        logger.exception("Erro ao obter todos os funcionários.")
        raise HTTPException(status_code=500, detail="Erro ao obter funcionários")

@router.post("/", response_model=EmployeeRead)
def create_employee(employee: EmployeeCreate, session: Session = Depends(get_session)):
    logger.debug(f"Tentando criar funcionário: {employee}")
    db_employee = Employee(**employee.dict())
    try:
        session.add(db_employee)
        session.commit()
        session.refresh(db_employee)
        logger.info(f"Funcionário criado com sucesso: {db_employee}")
        return db_employee
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Erro ao criar funcionário")
        raise HTTPException(status_code=500, detail="Erro ao criar funcionário")

def get_employee(employee_id: int, session: Session) -> Employee:
    employee = session.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        logger.warning(f"Funcionário com ID {employee_id} não encontrado.")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee

@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, update: EmployeeUpdate, session: Session = Depends(get_session)):
    db_employee = get_employee(employee_id, session)
    for key, value in update.dict(exclude_unset=True).items():
        setattr(db_employee, key, value)
    try:
        session.commit()
        session.refresh(db_employee)
        logger.info(f"Funcionário ID {employee_id} atualizado com sucesso.")
        return db_employee
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao atualizar funcionário ID {employee_id}")
        raise HTTPException(status_code=500, detail="Erro ao atualizar funcionário")

@router.delete("/{employee_id}")
def delete_employee(employee_id: int, session: Session = Depends(get_session)):
    db_employee = get_employee(employee_id, session)
    try:
        session.delete(db_employee)
        session.commit()
        logger.info(f"Funcionário ID {employee_id} deletado com sucesso.")
        return {"message": "Funcionário deletado com sucesso"}
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao deletar funcionário ID {employee_id}")
        raise HTTPException(status_code=500, detail="Erro ao deletar funcionário")

@router.get("/search/{name}", response_model=List[EmployeeRead])
def search_employee_by_name(name: str, session: Session = Depends(get_session)):
    employees = session.query(Employee).filter(Employee.name.ilike(f"%{name}%")).all()
    if not employees:
        logger.warning(f"Nenhum funcionário encontrado com o nome: {name}")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/count")
def count_employees(session: Session = Depends(get_session)):
    """
    Retorna a quantidade total de funcionários cadastrados.
    """
    try:
        total = session.query(Employee).count()
        logger.info(f"Quantidade total de funcionários: {total}")
        return {"quantidade": total}
    except SQLAlchemyError:
        logger.exception("Erro ao contar funcionários")
        raise HTTPException(status_code=500, detail="Erro ao contar funcionários")

@router.get("/department/admission_date", response_model=List[EmployeeRead])
def get_employee_by_admission_date(admission_date: str, session: Session = Depends(get_session)):
    date = session.query(Employee).filter(Employee.admission_date.ilike(f"%{admission_date}%")).all()
    if not date:
        logger.warning(f"Nenhum funcionário encontrado com admitido em '{admission_date}'")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return date

@router.get("/department/{department_id}", response_model=List[EmployeeRead])
def get_employees_by_department(department_id: int, session: Session = Depends(get_session)):
    employees = session.query(Employee).filter(Employee.department_id == department_id).all()
    if not employees:
        logger.warning(f"Nenhum funcionário encontrado no departamento ID {department_id}")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/position/{position}", response_model=List[EmployeeRead])
def get_employees_by_position(position: str, session: Session = Depends(get_session)):
    employees = session.query(Employee).filter(Employee.position.ilike(f"%{position}%")).all()
    if not employees:
        logger.warning(f"Nenhum funcionário encontrado com cargo '{position}'")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employees

@router.get("/search", response_model=List[EmployeeRead])
def search_employees(name: Optional[str] = None, position: Optional[str] = None, session: Session = Depends(get_session)):
    query = session.query(Employee)
    if name:
        query = query.filter(Employee.name.ilike(f"%{name}%"))
    if position:
        query = query.filter(Employee.position.ilike(f"%{position}%"))
    
    employees = query.all()
    if not employees:
        logger.warning("Nenhum funcionário encontrado com os critérios fornecidos.")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    
    return employees

@router.get("/paginated", response_model=List[Employee])
def get_employee_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session=Depends(get_session)
):
    """
    Retorna departamentos funcionários
    """
    logger.debug(f"Buscando funcionários página {page} com limite {limit}")
    try:
        offset = (page - 1) * limit
        employes = session.query(Employee).offset(offset).limit(limit).all()
        logger.info(f"{len(employes)} funcionários recuperados na página {page}")
        return employes
    except SQLAlchemyError:
        logger.exception("Erro ao listar funcionários paginados")
        raise HTTPException(status_code=500, detail="Erro interno ao listar funcionários")

@router.get("/filtered", response_model=List[EmployeeRead])
def filter_employees(
    name: Optional[str] = Query(None, description="Busca parcial no nome (case-insensitive)"),
    position: Optional[str] = Query(None, description="Busca parcial no cargo (case-insensitive)"),
    cpf: Optional[str] = Query(None, description="CPF completo ou parcial"),
    min_admission_date: Optional[str] = Query(None, description="Data mínima de admissão (AAAA-MM-DD)"),
    max_admission_date: Optional[str] = Query(None, description="Data máxima de admissão (AAAA-MM-DD)"),
    department_id: Optional[int] = Query(None, description="ID do departamento"),
    session: Session = Depends(get_session)
):
    """
    Filtra funcionários por múltiplos atributos com suporte a intervalo de datas.
    
    Parâmetros:
    - name: Busca parcial no nome
    - position: Busca parcial no cargo
    - cpf: Busca parcial no CPF
    - min_admission_date: Data mínima de admissão (inclusive)
    - max_admission_date: Data máxima de admissão (inclusive)
    - department_id: ID exato do departamento
    
    Exemplos:
    - /employees/filtered?name=maria&position=gerente
    - /employees/filtered?min_admission_date=2020-01-01&max_admission_date=2022-12-31
    - /employees/filtered?department_id=5
    """
    try:
        logger.debug(f"Filtrando funcionários com parâmetros: name={name}, position={position}, "
                     f"cpf={cpf}, min_admission_date={min_admission_date}, "
                     f"max_admission_date={max_admission_date}, department_id={department_id}")
        
        query = session.query(Employee)
        
        # Aplicar filtros
        if name:
            query = query.filter(Employee.name.ilike(f"%{name}%"))
        if position:
            query = query.filter(Employee.position.ilike(f"%{position}%"))
        if cpf:
            query = query.filter(Employee.cpf.ilike(f"%{cpf}%"))
        if min_admission_date:
            query = query.filter(Employee.admission_date >= min_admission_date)
        if max_admission_date:
            query = query.filter(Employee.admission_date <= max_admission_date)
        if department_id is not None:
            query = query.filter(Employee.department_id == department_id)
        
        employees = query.all()
        
        if not employees:
            logger.info("Nenhum funcionário encontrado com os filtros especificados")
            raise HTTPException(
                status_code=404,
                detail="Nenhum funcionário encontrado com os critérios de filtro"
            )
        
        logger.info(f"{len(employees)} funcionários encontrados com os filtros")
        return employees
    
    except ValueError as ve:
        logger.error(f"Erro de formato de data: {str(ve)}")
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use AAAA-MM-DD"
        )
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao filtrar funcionários: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao filtrar funcionários"
        )

@router.get("/{employee_id}", response_model=EmployeeRead)
def read_employee(employee_id: int, session: Session = Depends(get_session)):
    employee = session.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        logger.warning(f"Funcionário com ID {employee_id} não encontrado.")
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return employee