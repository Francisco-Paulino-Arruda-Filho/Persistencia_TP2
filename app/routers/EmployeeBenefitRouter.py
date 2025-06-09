from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlmodel import select

from app.core.db import get_session
from app.logs.logger import logger
from app.models import EmployeeBenefit, Employee, Benefit
from app.models.EmployeeBenefit import EmployeeBenefitRead, EmployeeBenefitCreate, EmployeeBenefitUpdate

router = APIRouter(prefix="/employee-benefits", tags=["Benefícios dos Funcionários"])

@router.post("/", response_model=EmployeeBenefitRead)
def create_employee_benefit(
    employee_benefit: EmployeeBenefitCreate,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para criar novo Benefício dos Funcionários: {employee_benefit}")
    try:
        validate_employee_benefit(None, employee_benefit, session)

        db_employee_benefit = EmployeeBenefit(**employee_benefit.dict())
        session.add(db_employee_benefit)
        session.commit()
        session.refresh(db_employee_benefit)
        logger.info(f"Benefício dos Funcionários criada com sucesso: {db_employee_benefit}")
        return db_employee_benefit
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao criar Benefício dos Funcionários")
        raise HTTPException(status_code=500, detail="Erro interno ao criar Benefício dos Funcionários")

@router.get("/", response_model=List[EmployeeBenefitRead])
def get_all_employee_benefits(
    session: Session = Depends(get_session)
):
    logger.debug("Solicitação para listar todos os Benefícios dos Funcionários")
    try:
        employee_benefits = session.exec(select(EmployeeBenefit)).all()
        logger.info(f"Benefícios dos Funcionários listados com sucesso: {employee_benefits}")
        return employee_benefits
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao listar todos os Benefícios dos Funcionários")
        raise HTTPException(status_code=500, detail="Erro interno ao listar todos os Benefícios dos Funcionários")

@router.put("/{employee_benefit_id}", response_model=EmployeeBenefitRead)
def update_employee_benefit(
    employee_benefit_id: int,
    employee_benefit: EmployeeBenefitUpdate,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para atualizar Benefício dos Funcionários: {employee_benefit_id}")

    db_employee_benefit = session.query(EmployeeBenefit).filter(EmployeeBenefit.id == employee_benefit_id).first()
    validate_employee_benefit(employee_benefit_id, employee_benefit, session)
    update_data = employee_benefit.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_employee_benefit, key, value)

    session.commit()
    session.refresh(db_employee_benefit)
    logger.info(f"FBenefício dos Funcionários atualizado com sucesso: {employee_benefit_id}")
    return db_employee_benefit

@router.delete("/{employee_benefit_id}")
def delete_employee_benefit(
    employee_benefit_id: int,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para deletar Benefício dos Funcionários: {employee_benefit_id}")

    try:
        employee_benefit = session.query(EmployeeBenefit).filter(EmployeeBenefit.id == employee_benefit_id).first()
        validate_employee_benefit(employee_benefit_id, None, session)
        session.delete(employee_benefit)
        session.commit()
        logger.info(f"Benefício do Funcionário deletado com sucesso: {employee_benefit_id}")
        return {"message": "Benefício do Funcionário deletado com sucesso"}

    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao deletar Benefício do Funcionário")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar Benefício do Funcionário")

@router.get("/count", summary="Quantidade de Benefícios dos Funcionários")
def count_employee_benefits(
    session = Depends(get_session)
):
    logger.debug("Solicitação para contar os Benefícios dos Funcionários")

    try:
        count = session.query(EmployeeBenefit).count()
        logger.info(f"Quantidade total de Benefícios dos Funcionários: {count}")
        return {"quantidade": count}
    except SQLAlchemyError:
        logger.exception(f"Erro ao contar Benefícios dos Funcionários")
        raise HTTPException(status_code=500, detail="Erro interno ao contar Benefícios dos Funcionários")

@router.get("/paginated")
def get_employee_benefits_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session = Depends(get_session)
):
    logger.debug("Solicitação para buscar Benefícios dos Funcionários")
    try:
        offset = (page - 1) * limit
        employee_benefits = session.query(EmployeeBenefit).offset(offset).limit(limit).all()
        logger.info(f"{len(employee_benefits)} Benefícios dos Funcionários recuperados na página {page}")
        return employee_benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao recuperar Benefícios dos Funcionários")
        raise HTTPException(status_code=500, detail="Erro interno ao recuperar Benefícios dos Funcionários")

@router.get("/{employee_benefit_id}", response_model=EmployeeBenefitRead)
def get_employee_benefit(
    employee_benefit_id: int,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para recuperar Benefício do Funcionário: {employee_benefit_id}")
    try:
        db_employee_benefit = session.query(EmployeeBenefit).filter(EmployeeBenefit.id == employee_benefit_id).first()
        validate_employee_benefit(employee_benefit_id, None, session)
        logger.info(f"Benefícios dos Funcionários recuperado: {db_employee_benefit}")
        return db_employee_benefit
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao recuperar Benefício do Funcionário")
        raise HTTPException(status_code=500, detail="Erro interno ao recuperar Benefício do Funcionário")

def validate_employee_benefit(
    employee_benefit_id: int = None,
    employee_benefit: EmployeeBenefitCreate | EmployeeBenefitUpdate = None,
    session: Session = None
):
    if employee_benefit_id is not None:
        db_employee_benefit = session.query(EmployeeBenefit).filter(EmployeeBenefit.id == employee_benefit_id).first()
        if not db_employee_benefit:
            logger.warning(f"Benefício dos Funcionário com ID {db_employee_benefit} não encontrado")
            raise HTTPException(status_code=404, detail="Benefícios dos Funcionários não encontrado")

    if employee_benefit is not None:
        employee = session.query(Employee).filter(Employee.id == employee_benefit.employee_id).first()
        if not employee:
            logger.warning(f"Funcionário com ID {employee_benefit.employee_id} não encontrada")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        benefit = session.query(Benefit).filter(Benefit.id == employee_benefit.benefit_id).first()
        if not benefit:
            logger.warning(f"Benefício com ID {employee_benefit.benefit_id} não encontrada")
            raise HTTPException(status_code=404, detail="Benefício não encontrado")
