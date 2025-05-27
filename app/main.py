from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Importa o middleware

from app.cadastro import router as cadastro_router
from app.login import router as login_router
from app.plantas import router as plantas_router
from app.ranking import router as ranking_router

app = FastAPI(title="API Jardim Botânico")

# Lista de origens permitidas (seu front)
origins = [
    "https://pedro-henrique-jv.github.io",
    # se quiser testar local, pode adicionar "http://localhost:5500"
]

# Adiciona o middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # ou ["*"] para liberar tudo (teste)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cadastro_router, prefix="/usuarios", tags=["Cadastro"])
app.include_router(login_router, prefix="/login", tags=["Login"])
app.include_router(plantas_router, prefix="/plantas", tags=["Plantas"])
app.include_router(ranking_router, prefix="/ranking", tags=["Ranking"])
