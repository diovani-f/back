from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, constr
import databases
import sqlalchemy
import bcrypt
from datetime import datetime
import os

router = APIRouter()

DATABASE_URL = "postgresql://jardimdb_ivqn_user:yrlylv8SVjnihgHkai8EBTTlVh9EXva0@dpg-d1fvro6mcj7s73c6f50g-a.oregon-postgres.render.com/jardimdb_ivqn"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

usuarios = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nome", sqlalchemy.String(length=100), nullable=False),
    sqlalchemy.Column("email", sqlalchemy.String(length=100), nullable=False, unique=True),
    sqlalchemy.Column("senha", sqlalchemy.String(length=255), nullable=False),
    sqlalchemy.Column("data_cadastro", sqlalchemy.DateTime, default=datetime.utcnow),
)

class UsuarioCreate(BaseModel):
    nome: constr(min_length=3, max_length=100)
    email: EmailStr
    senha: constr(min_length=6, max_length=100)

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def cadastrar_usuario(usuario: UsuarioCreate):
    hashed_senha = bcrypt.hashpw(usuario.senha.encode("utf-8"), bcrypt.gensalt())
    query = usuarios.insert().values(
        nome=usuario.nome,
        email=usuario.email,
        senha=hashed_senha.decode("utf-8"),
        data_cadastro=datetime.utcnow()
    )
    try:
        usuario_id = await database.execute(query)
        return {"id": usuario_id, "nome": usuario.nome, "email": usuario.email}
    except Exception as e:
        if "duplicate key value violates unique constraint" in str(e):
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")
