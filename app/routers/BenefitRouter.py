
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, func, select
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
    except SQLAlchemyError:
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
    except SQLAlchemyError:
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
    except SQLAlchemyError:
        logger.exception("Erro ao pesquisar benefícios")
        raise HTTPException(status_code=500, detail="Erro interno ao pesquisar benefícios")
    
@router.get("/count", summary="Quantidade de benefícios")
def count_benefits(session: Session = Depends(get_session)):
    """
    Retorna a quantidade total de benefícios cadastrados.
    """
    logger.debug("Solicitação para contar benefícios")
    try:
        quantidade = session.query(Benefit).count()
        logger.info(f"Quantidade total de benefícios: {quantidade}")
        return {"quantidade": quantidade}
    except SQLAlchemyError:
        logger.exception("Erro ao contar benefícios")
        raise HTTPException(status_code=500, detail="Erro interno ao contar benefícios")
    
@router.get("/paginated", response_model=List[Benefit])
def get_benefit_paginated(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    session=Depends(get_session)
):
    """
    Retorna benefícios paginados
    """
    logger.debug(f"Buscando beneficios página {page} com limite {limit}")
    try:
        offset = (page - 1) * limit
        benefits = session.query(Benefit).offset(offset).limit(limit).all()
        logger.info(f"{len(benefits)} benefícios recuperados na página {page}")
        return benefits
    except SQLAlchemyError:
        logger.exception("Erro ao listar benefícios paginados")
        raise HTTPException(status_code=500, detail="Erro interno ao lisar benefícios")
    
# Endpoint para buscar benefícios por ID exato
@router.get("/by-id/{benefit_id}", response_model=BenefitRead)
def get_benefit_by_id(
    benefit_id: int, 
    session: Session = Depends(get_session)
):
    """
    Busca um benefício específico pelo ID exato
    """
    try:
        benefit = session.get(Benefit, benefit_id)
        if not benefit:
            logger.warning(f"Benefício com ID {benefit_id} não encontrado")
            raise HTTPException(status_code=404, detail="Benefício não encontrado")
        return benefit
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefício por ID {benefit_id}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefício")

# Endpoint para buscar benefícios por nome (busca parcial case-insensitive)
@router.get("/by-name/{name}", response_model=List[BenefitRead])
def get_benefits_by_name(
    name: str,
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por nome (busca parcial case-insensitive)
    """
    try:
        benefits = session.exec(
            select(Benefit).where(Benefit.name.ilike(f"%{name}%"))
        ).all()
        if not benefits:
            raise HTTPException(status_code=404, detail="Nenhum benefício encontrado")
        return benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefícios por nome: {name}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")

# Endpoint para buscar benefícios por tipo exato
@router.get("/by-type/{type}", response_model=List[BenefitRead])
def get_benefits_by_type(
    type: str,
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por tipo exato
    """
    try:
        benefits = session.exec(
            select(Benefit).where(Benefit.type == type)
        ).all()
        if not benefits:
            raise HTTPException(status_code=404, detail="Nenhum benefício encontrado")
        return benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefícios por tipo: {type}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")

# Endpoint para buscar benefícios por valor exato
@router.get("/by-amount/{amount}", response_model=List[BenefitRead])
def get_benefits_by_amount(
    amount: float,
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por valor exato
    """
    try:
        benefits = session.exec(
            select(Benefit).where(Benefit.amount == amount)
        ).all()
        if not benefits:
            raise HTTPException(status_code=404, detail="Nenhum benefício encontrado")
        return benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefícios por valor: {amount}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")

# Endpoint para buscar benefícios por status (ativo/inativo)
@router.get("/by-active/{active}", response_model=List[BenefitRead])
def get_benefits_by_active_status(
    active: bool,
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por status ativo/inativo
    """
    try:
        benefits = session.exec(
            select(Benefit).where(Benefit.active == active)
        ).all()
        if not benefits:
            status = "ativos" if active else "inativos"
            raise HTTPException(status_code=404, detail=f"Nenhum benefício {status} encontrado")
        return benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefícios por status: {active}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")

# Endpoint para buscar benefícios por descrição (busca parcial)
@router.get("/by-description/{description}", response_model=List[BenefitRead])
def get_benefits_by_description(
    description: str,
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por descrição (busca parcial case-insensitive)
    """
    try:
        benefits = session.exec(
            select(Benefit).where(Benefit.description.ilike(f"%{description}%"))
        ).all()
        if not benefits:
            raise HTTPException(status_code=404, detail="Nenhum benefício encontrado")
        return benefits
    except SQLAlchemyError:
        logger.exception(f"Erro ao buscar benefícios por descrição: {description}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")

@router.get("/sorted-by-amount", response_model=List[BenefitRead])
def get_benefits_sorted_by_amount(
    order: str = Query("asc", regex="^(asc|desc)$"),
    session: Session = Depends(get_session)
):
    """
    Retorna os benefícios ordenados pelo valor (amount) em ordem crescente ou decrescente.
    """
    logger.debug(f"Solicitação para listar benefícios ordenados por amount em ordem: {order}")
    try:
        query = select(Benefit).order_by(
            Benefit.amount.asc() if order == "asc" else Benefit.amount.desc()
        )
        benefits = session.exec(query).all()
        logger.info(f"{len(benefits)} benefícios ordenados por amount retornados")
        return benefits
    except SQLAlchemyError:
        logger.exception("Erro ao ordenar benefícios por amount")
        raise HTTPException(status_code=500, detail="Erro interno ao ordenar benefícios")


# Endpoint para buscar benefícios por faixa de valor
@router.get("/by-amount-range/", response_model=List[BenefitRead])
def get_benefits_by_amount_range(
    min_amount: float = Query(...),
    max_amount: float = Query(...),
    session: Session = Depends(get_session)
):
    """
    Busca benefícios por faixa de valor (inclusivo)
    """
    try:
        benefits = session.exec(
            select(Benefit).where(
                Benefit.amount >= min_amount,
                Benefit.amount <= max_amount
            )
        ).all()
        if not benefits:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum benefício encontrado entre {min_amount} e {max_amount}"
            )
        return benefits
    except SQLAlchemyError:
        logger.exception("Erro ao buscar benefícios por faixa de valor")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefícios")
    
@router.get("/benefits/count-by-type")
def count_benefits_by_type(session: Session = Depends(get_session)):
    statement = (
        select(
            Benefit.type,
            func.count(Benefit.id).label("count")
        )
        .group_by(Benefit.type)
    )
    
    results = session.exec(statement).all()
    
    return [{"type": r[0], "count": r[1]} for r in results]

@router.get("/filtered", response_model=List[BenefitRead])
def filter_benefits(
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    type: Optional[str] = Query(None),
    active: Optional[bool] = Query(None),
    session: Session = Depends(get_session)
):
    """
    Filtra benefícios por múltiplos atributos com suporte a intervalo de valores.
    
    Parâmetros:
    - name: Busca parcial no nome (case-insensitive)
    - description: Busca parcial na descrição (case-insensitive)
    - min_amount: Valor mínimo do benefício (inclusive)
    - max_amount: Valor máximo do benefício (inclusive)
    - type: Tipo exato do benefício
    - active: Status ativo/inativo
    
    Exemplos:
    - /benefits/filtered?name=saude&min_amount=100&max_amount=500
    - /benefits/filtered?type=plano&active=true
    """
    logger.debug("Filtrando benefícios com parâmetros: "
                 f"name={name}, description={description}, "
                 f"min_amount={min_amount}, max_amount={max_amount}, "
                 f"type={type}, active={active}")
    
    try:
        query = select(Benefit)
        
        # Filtros
        if name:
            query = query.where(Benefit.name.ilike(f"%{name}%"))
        if description:
            query = query.where(Benefit.description.ilike(f"%{description}%"))
        if min_amount is not None:
            query = query.where(Benefit.amount >= min_amount)
        if max_amount is not None:
            query = query.where(Benefit.amount <= max_amount)
        if type:
            query = query.where(Benefit.type == type)
        if active is not None:
            query = query.where(Benefit.active == active)
        
        benefits = session.exec(query).all()
        
        if not benefits:
            logger.info("Nenhum benefício encontrado com os filtros especificados")
            raise HTTPException(
                status_code=404,
                detail="Nenhum benefício encontrado com os critérios de filtro"
            )
        
        logger.info(f"{len(benefits)} benefícios encontrados com os filtros")
        return benefits
    
    except SQLAlchemyError as e:
        logger.exception(f"Erro ao filtrar benefícios: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao filtrar benefícios"
        )

    
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
    except SQLAlchemyError:
        logger.exception("Erro ao buscar benefício por ID")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar benefício")
