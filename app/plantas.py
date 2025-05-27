from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
import databases
import sqlalchemy
import os
from datetime import datetime
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()

DATABASE_URL = "postgresql://diovani:Ji7huPzuwV9wxDTimf3TgXKrvIhH6e6X@dpg-d0qgcsjipnbc73ebvoeg-a.oregon-postgres.render.com:5432/jardimdb"

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

plantas_pegas = sqlalchemy.Table(
    "plantas_pegas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("usuario_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("especie_id", sqlalchemy.String(length=100), nullable=False),
    sqlalchemy.Column("pontos", sqlalchemy.Integer, default=10),
    sqlalchemy.Column("data_coleta", sqlalchemy.DateTime, default=datetime.utcnow),
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

class PlantaPegaCreate(BaseModel):
    especie_id: constr(min_length=1, max_length=100)

def get_usuario_id(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload.get("sub"))
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def inserir_planta_pegada(planta: PlantaPegaCreate, usuario_id: int = Depends(get_usuario_id)):
    query = plantas_pegas.insert().values(
        usuario_id=usuario_id,
        especie_id=planta.especie_id,
        pontos=10,
        data_coleta=datetime.utcnow()
    )
    try:
        planta_id = await database.execute(query)
        return {"id": planta_id, "usuario_id": usuario_id, "especie_id": planta.especie_id}
    except Exception as e:
        if "unique_usuario_especie" in str(e):
            raise HTTPException(status_code=400, detail="Você já coletou essa planta")
        raise HTTPException(status_code=500, detail="Erro interno no servidor")

@router.get("/", status_code=status.HTTP_200_OK)
async def listar_plantas_pegas(usuario_id: int = Depends(get_usuario_id)):
    query = plantas_pegas.select().where(plantas_pegas.c.usuario_id == usuario_id)
    plantas = await database.fetch_all(query)
    return plantas
