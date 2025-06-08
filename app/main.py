from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.cadastro import router as cadastro_router
from app.login import router as login_router
from app.plantas import router as plantas_router
from app.ranking import router as ranking_router
from app.quiz import router as quiz_router

app = FastAPI(title="API Jardim Botânico")

# Lista de origens permitidas (coloque sua URL do frontend)
origins = [
    "https://pedro-henrique-jv.github.io",
    # "http://localhost:5500",  # para testes locais, se quiser
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(cadastro_router, prefix="/usuarios", tags=["Cadastro"])
app.include_router(login_router, prefix="/login", tags=["Login"])
app.include_router(plantas_router, prefix="/plantas", tags=["Plantas"])
app.include_router(ranking_router, prefix="/ranking", tags=["Ranking"])
app.include_router(quiz_router, prefix="/quiz", tags=["Quiz"])  # ⬅️ Aqui adiciona o quiz
