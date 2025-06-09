from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select
from app.core.db import get_session
from app.logs.logger import logger
from app.models import Employee
from app.models.Payroll import PayrollCreate, PayrollRead, Payroll, PayrollUpdate

router = APIRouter(prefix="/pay_rolls", tags=["Folhas de Pagamento"])

@router.post("/", response_model=PayrollRead)
def create_payroll(
    payroll: PayrollCreate,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para criar nova folha de pagamento: {payroll}")
    try:
        employee = session.query(Employee).filter(Employee.id == payroll.employee_id).first()
        if not employee:
            logger.warning(f"Funcionário com ID {payroll.employee_id} não encontrada")
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")

        db_payroll = Payroll(**payroll.dict())
        session.add(db_payroll)
        session.commit()
        session.refresh(db_payroll)
        logger.info(f"Folha de Pagamento criada com sucesso: {payroll}")
        return db_payroll
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao criar folha de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao criar folha de pagamento")

@router.get("/", response_model=List[PayrollRead])
def get_all_payrolls(
    session: Session = Depends(get_session)
):
    logger.debug("Solicitação para listar todas as folhas de pagamento")
    try:
        payrolls = session.exec(select(Payroll)).all()
        logger.info(f"Folhas de pagamento listadas com sucesso: {payrolls}")
        return payrolls
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao listar todas as folhas de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao listar todas as folhas de pagamento")

@router.put("/{payroll_id}", response_model=PayrollRead)
def update_payroll(
    payroll_id: int,
    payroll: PayrollUpdate,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para atualizar folha de pagamento: {payroll_id}")

    db_payroll = session.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not db_payroll:
        logger.warning(f"Folha de pagamento com ID {payroll_id} não encontrada")
        raise HTTPException(status_code=404, detail="Folha de pagamento não encontrada")

    update_data = payroll.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payroll, key, value)

    session.commit()
    session.refresh(db_payroll)
    logger.info(f"Folha de pagamento atualizada com sucesso: {payroll_id}")
    return db_payroll

@router.delete("/{payroll_id}")
def delete_payroll(
    payroll_id: int,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para deletar folha de pagamento: {payroll_id}")

    try:
        payroll = session.query(Payroll).filter(Payroll.id == payroll_id).first()
        if not payroll:
            logger.warning(f"Folha de pagamento com ID {payroll_id} não encontrada")
            raise HTTPException(status_code=404, detail="Folha de pagamento não encontrada")

        session.delete(payroll)
        session.commit()
        logger.info(f"Folha de pagamento deletada com sucesso: {payroll_id}")
        return {"message": "Folha de pagamento deletada com sucesso"}

    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao deletar folha de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar folha de pagamento")

@router.get("/count", summary="Quantidade de Folhas de Pagamentos")
def count_payrolls(
    session = Depends(get_session)
):
    logger.debug("Solicitação para contar as folhas de pagamento")

    try:
        count = session.query(Payroll).count()
        logger.info(f"Quantidade total de Folhas de Pagamentos: {count}")
        return {"quantidade": count}
    except SQLAlchemyError:
        logger.exception(f"Erro ao contar folha de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao contar folha de pagamento")

@router.get("/paginated")
def get_payrolls_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session = Depends(get_session)
):
    logger.debug("Solicitação para buscar folhas de pagamento")
    try:
        offset = (page - 1) * limit
        payrolls = session.query(Payroll).offset(offset).limit(limit).all()
        logger.info(f"{len(payrolls)} Folhas de pagamentos recuperadas na página {page}")
        return payrolls
    except SQLAlchemyError:
        logger.exception(f"Erro ao recuperar folhas de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao recuperar folhas de pagamento")

@router.get("/{payroll_id}", response_model=PayrollRead)
def get_payroll(
    payroll_id: int,
    session = Depends(get_session)
):
    logger.debug(f"Solicitação para recuperar folha de pagamento: {payroll_id}")
    try:
        payroll = session.query(Payroll).filter(Payroll.id == payroll_id).first()
        if not payroll:
            logger.warning(f"Folha de pagamento com ID {payroll_id} não encontrada")
            raise HTTPException(status_code=404, detail="Folha de pagamento não encontrada")
        logger.info(f"Folha de pagamento recuperada: {payroll}")
        return payroll
    except SQLAlchemyError:
        session.rollback()
        logger.exception(f"Erro ao recuperar folha de pagamento")
        raise HTTPException(status_code=500, detail="Erro interno ao recuperar folha de pagamento")
