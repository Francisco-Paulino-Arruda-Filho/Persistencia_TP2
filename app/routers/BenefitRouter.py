
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session
from app.models.Benefit import Benefit, BenefitCreate, BenefitRead
from ..core.db import get_session
from ..logs.logger import logger


router = APIRouter(prefix="/benefits", tags=["Benefícios"])



@router.post("/", response_model=BenefitRead)
def create_benefit(benefit: BenefitCreate, session: Session = Depends(get_session)):
    """
    Cria um novo benefício.
    """
    logger.debug(f"Tentando criar benefício: {benefit}")
    try:
        db_benefit = Benefit.from_orm(benefit)
        session.add(db_benefit)
        session.commit()
        session.refresh(db_benefit)
        logger.info(f"Benefício criado com sucesso: {db_benefit}")
        return db_benefit
    except SQLAlchemyError:
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
    
@router.put("/{benefit_id}", response_model=BenefitRead)
def update_benefit(benefit_id: int, benefit: BenefitCreate, session: Session = Depends(get_session)):
    """
    Atualiza um benefício existente.
    """
    db_benefit = session.query(Benefit).filter(Benefit.id == benefit_id).first()
    if not db_benefit:
        logger.warning(f"Benefício com ID {benefit_id} não encontrado para atualização.")
        raise HTTPException(status_code=404, detail="Benefício não encontrado")
    
    update_data = benefit.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_benefit, key, value)
    
    session.commit()
    session.refresh(db_benefit)
    logger.info(f"Benefício atualizado com sucesso: {db_benefit}")
    return db_benefit

@router.delete("/{benefit_id}")
def delete_benefit(benefit_id: int, session: Session = Depends(get_session)):
    """
    Deleta um benefício pelo ID.
    """
    logger.debug(f"Tentando deletar benefício com ID {benefit_id}")
    try:
        benefit = session.query(Benefit).filter(Benefit.id == benefit_id).first()
        if not benefit:
            logger.warning(f"Benefício com ID {benefit_id} não encontrado.")
            raise HTTPException(status_code=404, detail="Benefício não encontrado")
        
        session.delete(benefit)
        session.commit()
        logger.info(f"Benefício deletado com sucesso: ID {benefit_id}")
        return {"message": "Benefício deletado com sucesso"}
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception("Erro ao deletar benefício")
        raise HTTPException(status_code=500, detail="Erro interno ao deletar benefício")
    
@router.get("/", response_model=list[BenefitRead])
def get_all_benefits(session: Session = Depends(get_session)):
    """
    Obtém todos os benefícios.
    """
    logger.debug("Solicitação para listar todos os benefícios")
    try:
        benefits = session.query(Benefit).all()
        logger.debug(f"Benefícios recuperados com sucesso: {benefits}")
        return benefits
    except SQLAlchemyError as e:
        logger.exception("Erro ao listar benefícios")
        raise HTTPException(status_code=500, detail="Erro interno ao listar benefícios")
    
@router.get("/search", response_model=list[BenefitRead])
def search_benefits(name: str = None, session: Session = Depends(get_session)):
    """
    Pesquisa benefícios pelo nome.
    """
    logger.debug(f"Solicitação de pesquisa de benefícios com nome: {name}")
    try:
        query = session.query(Benefit)
        if name:
            query = query.filter(Benefit.name.ilike(f"%{name}%"))
        
        benefits = query.all()
        logger.debug(f"Benefícios encontrados: {benefits}")
        return benefits
    except SQLAlchemyError as e:
        logger.exception("Erro ao pesquisar benefícios")
        raise HTTPException(status_code=500, detail="Erro interno ao pesquisar benefícios")
    
