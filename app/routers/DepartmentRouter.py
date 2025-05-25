from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.Department import Department
from ..core.db import get_session
from ..logs.logger import logger

router = APIRouter(prefix="/departments", tags=["Departamentos"])

@router.post("/", response_model=Department)
def create_department(department: Department, session=Depends(get_session)):
    """
    Cria um novo departamento.
    """
    logger.debug(f"Tentando criar departamento: {department}")
    try:
        session.add(department)
        session.commit()
        session.refresh(department)
        logger.info(f"Departamento criado com sucesso: {department}")
        return department
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

@router.get("/{department_id}", response_model=Department)
def read_department(department_id: int, session=Depends(get_session)):
    """
    Lê um departamento pelo ID.
    """
    logger.debug(f"Solicitação para ler departamento com ID {department_id}")
    return get_department(department_id, session)

@router.put("/{department_id}", response_model=Department)
def update_department(department_id: int, department: Department, session=Depends(get_session)):
    """
    Atualiza um departamento pelo ID.
    """
    logger.debug(f"Tentando atualizar departamento com ID {department_id}")
    try:
        db_department = get_department(department_id, session)
        for key, value in department.dict().items():
            setattr(db_department, key, value)
        session.commit()
        session.refresh(db_department)
        logger.info(f"Departamento atualizado com sucesso: {db_department}")
        return db_department
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Erro ao atualizar departamento")
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
