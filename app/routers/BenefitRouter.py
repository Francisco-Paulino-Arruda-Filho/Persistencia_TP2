
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.models.Benefit import Benefit
from ..core.db import get_session
from ..logs.logger import logger


router = APIRouter(prefix="/benefits", tags=["Benefícios"])

@router.post("/", response_model=Benefit)
def create_benefit(benefit: Benefit, session=Depends(get_session)):
    """
    Cria um novo benefício.
    """
    logger.debug(f"Tentando criar benefício: {benefit}")
    try:
        session.add(benefit)
        session.commit()
        session.refresh(benefit)
        logger.info(f"Benefício criado com sucesso: {benefit}")
        return benefit
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Erro ao criar benefício")
        raise HTTPException(status_code=500, detail="Erro interno ao criar benefício")

@router.get("/{benefit_id}", response_model=Benefit)
def get_benefit(benefit_id: int, session=Depends(get_session)):
    """
    Obtém um benefício pelo ID.
    """
    try:
        benefit = session.query(Benefit).filter(Benefit.id == benefit_id).first()
        if not benefit:
            logger.warning(f"Benefício com ID {benefit_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Benefício não encontrado")
        logger.debug(f"Benefício recuperado com sucesso: {benefit}")
        return benefit
    except SQLAlchemyError as e:
        logger.exception("Erro ao buscar benefício por ID")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefício")
    