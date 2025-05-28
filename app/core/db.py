from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

# Obtém a variável de ambiente DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Cria o engine com a URL do banco
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.commit()

def get_session():
    with Session(engine) as session:
        yield session
