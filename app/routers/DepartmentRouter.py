from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.models.Department import Department, DepartmentCreate, DepartmentRead, DepartmentUpdate
from app.models.Employee import Employee
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
        # Cria o objeto básico do departamento
        db_department = Department(
            name=department.name,
            location=department.location,
            description=department.description,
            extension=department.extension
        )
        
        # Se houver manager_id, associe o manager
        if department.manager_id:
            manager = session.get(Employee, department.manager_id)
            if not manager:
                raise HTTPException(status_code=404, detail="Manager não encontrado")
            db_department.manager = manager
        
        # Se houver employee_ids, associe os employees
        if department.employee_ids:
            employees = session.query(Employee).filter(Employee.id.in_(department.employee_ids)).all()
            if len(employees) != len(department.employee_ids):
                raise HTTPException(status_code=404, detail="Alguns funcionários não foram encontrados")
            db_department.employees = employees
        
        session.add(db_department)
        session.commit()
        session.refresh(db_department)
        logger.info(f"Departamento criado com sucesso: {db_department}")
        return db_department
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Erro ao criar departamento: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao criar departamento")

def get_department(department_id: int, session=Depends(get_session)):
    """
    Obtém um departamento pelo ID.
    """
    try:
        department = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.id == department_id).first()
        if not department:
            logger.warning(f"Departamento com ID {department_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")
        logger.debug(f"Departamento recuperado com sucesso: {department}")
        return department
    except SQLAlchemyError:
        logger.exception("Erro ao buscar departamento por ID")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento")

@router.put("/{department_id}", response_model=DepartmentRead)
def update_department(department_id: int, department: DepartmentUpdate, session=Depends(get_session)):
    """
    Atualiza um departamento incluindo manager e employees.
    """
    logger.debug(f"Tentando atualizar departamento ID {department_id}")
    try:
        # Carrega o departamento com todas as relações
        db_department = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.id == department_id).first()
        
        if not db_department:
            logger.warning(f"Departamento ID {department_id} não encontrado para atualização")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")

        update_data = department.dict(exclude_unset=True)
        
        # Atualizar campos simples
        for key, value in update_data.items():
            if key not in ['manager_id', 'employee_ids']:
                setattr(db_department, key, value)
        
        # Atualizar manager se fornecido
        if department.manager_id is not None:
            manager = session.get(Employee, department.manager_id)
            if not manager:
                raise HTTPException(status_code=404, detail="Manager não encontrado")
            db_department.manager = manager
        elif 'manager_id' in update_data and department.manager_id is None:
            # Permite remover o manager definindo como None
            db_department.manager = None
        
        # Atualizar employees se fornecido
        if department.employee_ids is not None:
            employees = session.query(Employee).filter(Employee.id.in_(department.employee_ids)).all()
            if len(employees) != len(department.employee_ids):
                raise HTTPException(status_code=404, detail="Alguns funcionários não foram encontrados")
            db_department.employees = employees
        
        session.commit()
        
        # Recarrega o departamento com todas as relações atualizadas
        session.refresh(db_department)
        db_department = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.id == department_id).first()
        
        logger.info(f"Departamento ID {department_id} atualizado com sucesso")
        return db_department
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Erro ao atualizar departamento ID {department_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar departamento")

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
    except SQLAlchemyError:
        session.rollback()
        logger.exception("Erro ao deletar departamento")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar departamento")

@router.get("/", response_model=list[DepartmentRead])
def get_all_departments(session=Depends(get_session)):
    """
    Obtém todos os departamentos.
    """
    logger.debug("Solicitação para listar todos os departamentos")
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).all()
        logger.info(f"{len(departments)} departamentos encontrados.")
        return departments
    except SQLAlchemyError:
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
    except SQLAlchemyError:
        logger.exception("Erro ao buscar departamento por nome")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento por nome")
    
@router.get("/by-name/{name}", response_model=List[DepartmentRead])
def get_departments_by_name(
    name: str,
    session=Depends(get_session)
):
    """
    Busca departamentos por nome (busca parcial case-insensitive)
    """
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.name.ilike(f"%{name}%")).all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado com nome contendo: {name}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados com nome contendo '{name}'")
        return departments
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamentos por nome: {name}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/by-location/{location}", response_model=List[DepartmentRead])
def get_departments_by_location(
    location: str,
    session=Depends(get_session)
):
    """
    Busca departamentos por localização (busca parcial case-insensitive)
    """
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.location.ilike(f"%{location}%")).all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado na localização contendo: {location}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados na localização contendo '{location}'")
        return departments
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamentos por localização: {location}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/by-description/{description}", response_model=List[DepartmentRead])
def get_departments_by_description(
    description: str,
    session=Depends(get_session)
):
    """
    Busca departamentos por descrição (busca parcial case-insensitive)
    """
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.description.ilike(f"%{description}%")).all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado com descrição contendo: {description}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados com descrição contendo '{description}'")
        return departments
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamentos por descrição: {description}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/by-extension/{extension}", response_model=DepartmentRead)
def get_department_by_extension(
    extension: str,
    session=Depends(get_session)
):
    """
    Busca departamento por ramal exato
    """
    try:
        department = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.extension == extension).first()
        
        if not department:
            logger.warning(f"Nenhum departamento encontrado com ramal: {extension}")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")
        
        logger.info(f"Departamento encontrado com ramal {extension}")
        return department
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamento por ramal: {extension}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento")

@router.get("/by-manager/{manager_id}", response_model=List[DepartmentRead])
def get_departments_by_manager(
    manager_id: int,
    session=Depends(get_session)
):
    """
    Busca departamentos gerenciados por um funcionário específico
    """
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.manager_id == manager_id).all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado gerenciado pelo funcionário ID: {manager_id}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados gerenciados pelo funcionário ID {manager_id}")
        return departments
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamentos por gerente: {manager_id}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/paginated", response_model=List[DepartmentRead])
def get_departments_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session=Depends(get_session)
):
    """
    Retorna departamentos paginados com informações de manager e employees
    """
    logger.debug(f"Buscando departamentos página {page} com limite {limit}")
    try:
        offset = (page - 1) * limit
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).offset(offset).limit(limit).all()
        
        logger.info(f"{len(departments)} departamentos recuperados na página {page}")
        return departments
    except SQLAlchemyError:
        logger.exception("Erro ao listar departamentos paginados")
        raise HTTPException(status_code=500, detail="Erro interno ao listar departamentos")
    
@router.get("/count", summary="Quantidade de departamentos")
def count_departments(session=Depends(get_session)):
    """
    Retorna a quantidade total de departamentos cadastrados.
    """
    logger.debug("Solicitação para contar departamentos")
    try:
        quantidade = session.query(Department).count()
        logger.info(f"Quantidade total de departamentos: {quantidade}")
        return {"quantidade": quantidade}
    except SQLAlchemyError:
        logger.exception("Erro ao contar departamentos")
        raise HTTPException(status_code=500, detail="Erro interno ao contar departamentos")

@router.get("/partial", response_model=List[DepartmentRead])
def get_departments_partial_name(
    name: str,
    session=Depends(get_session)
):
    """
    Busca departamentos por nome parcial (case-insensitive)
    """
    try:
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.name.ilike(f"%{name}%")).all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado com nome contendo: {name}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados com nome contendo '{name}'")
        return departments
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamentos por nome parcial: {name}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/by-employees/", response_model=List[DepartmentRead])
def get_departments_by_employees(
    employee_ids: List[int] = Query(..., description="Lista de IDs de funcionários para filtrar departamentos"),
    session=Depends(get_session)
):
    """
    Busca departamentos que contenham pelo menos um dos funcionários especificados.
    """
    logger.debug(f"Buscando departamentos com funcionários: {employee_ids}")
    try:
        # Verifica se todos os IDs de funcionários existem
        employees = session.query(Employee).filter(Employee.id.in_(employee_ids)).all()
        found_ids = {e.id for e in employees}
        missing_ids = set(employee_ids) - found_ids
        
        if missing_ids:
            logger.warning(f"Alguns funcionários não foram encontrados: {missing_ids}")
            raise HTTPException(
                status_code=404,
                detail=f"Funcionários não encontrados: {list(missing_ids)}"
            )
        
        # Busca departamentos que contenham pelo menos um dos funcionários
        departments = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).join(Department.employees).filter(Employee.id.in_(employee_ids)).distinct().all()
        
        if not departments:
            logger.warning(f"Nenhum departamento encontrado com os funcionários: {employee_ids}")
            raise HTTPException(status_code=404, detail="Nenhum departamento encontrado")
        
        logger.info(f"{len(departments)} departamentos encontrados com os funcionários especificados")
        return departments
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao buscar departamentos por funcionários: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamentos")

@router.get("/{department_id}", response_model=DepartmentRead)
def get_department_by_id(department_id: int, session=Depends(get_session)):
    """
    Busca um departamento pelo ID com todas as relações carregadas
    """
    logger.debug(f"Buscando departamento com ID {department_id}")
    try:
        department = session.query(Department).options(
            joinedload(Department.manager),
            joinedload(Department.employees)
        ).filter(Department.id == department_id).first()
        
        if not department:
            logger.warning(f"Departamento com ID {department_id} não encontrado")
            raise HTTPException(status_code=404, detail="Departamento não encontrado")
        
        logger.info(f"Departamento encontrado por ID: {department_id}")
        return department
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar departamento por ID: {department_id}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar departamento")
