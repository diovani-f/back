from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
import databases
import sqlalchemy
import bcrypt
import os
from jose import JWTError, jwt
from datetime import datetime, timedelta

router = APIRouter()

# URL de conexão com o banco
DATABASE_URL = "postgresql://diovani:Ji7huPzuwV9wxDTimf3TgXKrvIhH6e6X@dpg-d0qgcsjipnbc73ebvoeg-a.oregon-postgres.render.com:5432/jardimdb"

# Configurações do JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia

# Configuração do banco
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Definição da tabela de usuários
usuarios = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nome", sqlalchemy.String(length=100), nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String(length=100), nullable=False, unique=True),
    sqlalchemy.Column("senha", sqlalchemy.String(length=255), nullable=False),
    sqlalchemy.Column("data_cadastro", sqlalchemy.DateTime),
)

# Modelos Pydantic
class LoginData(BaseModel):
    email: EmailStr
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str
    nome: str  # Nome do usuário retornado no login

# Eventos de conexão com o banco
@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Rota de login
@router.post("/", response_model=Token)
async def login(data: LoginData):
    query = usuarios.select().where(usuarios.c.email == data.email)
    usuario = await database.fetch_one(query)

    if not usuario:
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    if not bcrypt.checkpw(data.senha.encode("utf-8"), usuario["senha"].encode("utf-8")):
        raise HTTPException(status_code=400, detail="Email ou senha inválidos")

    # Criar token JWT
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(usuario["id"]), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": encoded_jwt,
        "token_type": "bearer",
        "nome": usuario["nome"]
    }
