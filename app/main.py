from fastapi import FastAPI
from app.cadastro import router as cadastro_router
from app.login import router as login_router
from app.plantas import router as plantas_router
from app.ranking import router as ranking_router

app = FastAPI(title="API Jardim Botânico")

app.include_router(cadastro_router, prefix="/usuarios", tags=["Cadastro"])
app.include_router(login_router, prefix="/login", tags=["Login"])
app.include_router(plantas_router, prefix="/plantas", tags=["Plantas"])
app.include_router(ranking_router, prefix="/ranking", tags=["Ranking"])
