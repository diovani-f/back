from fastapi import APIRouter
import databases
import sqlalchemy
import os

router = APIRouter()

DATABASE_URL = "postgresql://diovani:Ji7huPzuwV9wxDTimf3TgXKrvIhH6e6X@dpg-d0qgcsjipnbc73ebvoeg-a.oregon-postgres.render.com:5432/jardimdb"


database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

plantas_pegas = sqlalchemy.Table(
    "plantas_pegas",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("usuario_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("especie_id", sqlalchemy.String(length=100), nullable=False),
    sqlalchemy.Column("pontos", sqlalchemy.Integer, default=10),
)

usuarios = sqlalchemy.Table(
    "usuarios",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nome", sqlalchemy.String(length=100), nullable=False),
)

@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@router.get("/")
async def ranking():
    query = """
        SELECT u.id, u.nome, COALESCE(SUM(p.pontos), 0) AS total_pontos
        FROM usuarios u
        LEFT JOIN plantas_pegas p ON u.id = p.usuario_id
        GROUP BY u.id
        ORDER BY total_pontos DESC
        LIMIT 10
    """
    resultados = await database.fetch_all(query=query)
    return resultados
