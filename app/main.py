import uvicorn
from fastapi import FastAPI

from app.core.db import create_db_and_tables
from app.routers.BenefitRouter import router as BenefitRouter
from app.routers.DepartmentRouter import router as DepartmentRouter
from app.routers.EmployeeRouter import router as EmployeeRouter
from app.routers.PayrollRouter import router as PayrollRouter
from app.routers.EmployeeBenefitRouter import router as EmployeeBenefitRouter

app = FastAPI()
app.include_router(BenefitRouter)
app.include_router(DepartmentRouter)
app.include_router(EmployeeRouter)
app.include_router(EmployeeBenefitRouter)
app.include_router(PayrollRouter)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
@app.get("/")
def home():
    return {"mensagem": "Bem vindo"}

if __name__=="__main__":
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True)