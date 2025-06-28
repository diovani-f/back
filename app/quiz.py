from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import databases
import sqlalchemy
import os
from datetime import datetime
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from enum import Enum

router = APIRouter()

# Configurações
DATABASE_URL = "postgresql://jardimdb_ivqn_user:yrlylv8SVjnihgHkai8EBTTlVh9EXva0@dpg-d1fvro6mcj7s73c6f50g-a.oregon-postgres.render.com/jardimdb_ivqn"
SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Tabela quiz
quiz = sqlalchemy.Table(
    "quiz",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("pergunta", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("alternativa_a", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("alternativa_b", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("alternativa_c", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("alternativa_d", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("resposta_correta", sqlalchemy.String(length=1), nullable=False),
)

# Tabela de perguntas respondidas
quiz_respondido = sqlalchemy.Table(
    "quiz_respondido",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("usuario_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("quiz_id", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("acertou", sqlalchemy.Boolean),
    sqlalchemy.Column("data_resposta", sqlalchemy.DateTime, default=datetime.utcnow),
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Modelos
class QuizOut(BaseModel):
    id: int
    pergunta: str
    alternativa_a: str
    alternativa_b: str
    alternativa_c: str
    alternativa_d: str
    resposta_correta: str

class AlternativaEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"

class RespostaQuizIn(BaseModel):
    quiz_id: int
    resposta: AlternativaEnum

# Utilitário: pegar usuário do token
def get_usuario_id(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload.get("sub"))
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return usuario_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Conexão com o banco
@router.on_event("startup")
async def startup():
    await database.connect()

@router.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Rota: Sorteio de pergunta
@router.get("/pergunta", response_model=QuizOut)
async def sortear_pergunta(usuario_id: int = Depends(get_usuario_id)):
    query = """
        SELECT * FROM quiz
        WHERE id NOT IN (
            SELECT quiz_id FROM quiz_respondido WHERE usuario_id = :usuario_id
        )
        ORDER BY RANDOM()
        LIMIT 1;
    """
    pergunta = await database.fetch_one(query, {"usuario_id": usuario_id})

    if not pergunta:
        raise HTTPException(status_code=404, detail="Você já respondeu todas as perguntas!")

    return pergunta

# Rota: Responder pergunta
@router.post("/responder")
async def responder_pergunta(
    dados: RespostaQuizIn,
    usuario_id: int = Depends(get_usuario_id)
):
    # Verifica se já respondeu
    query_check = quiz_respondido.select().where(
        (quiz_respondido.c.usuario_id == usuario_id) &
        (quiz_respondido.c.quiz_id == dados.quiz_id)
    )
    resposta_existente = await database.fetch_one(query_check)

    if resposta_existente:
        raise HTTPException(status_code=400, detail="Você já respondeu esta pergunta")

    # Busca pergunta
    query_quiz = quiz.select().where(quiz.c.id == dados.quiz_id)
    pergunta = await database.fetch_one(query_quiz)

    if not pergunta:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")

    acertou = dados.resposta.upper() == pergunta["resposta_correta"].upper()

    # Registra resposta
    query_insert = quiz_respondido.insert().values(
        usuario_id=usuario_id,
        quiz_id=dados.quiz_id,
        acertou=acertou,
        data_resposta=datetime.utcnow()
    )
    await database.execute(query_insert)

    if acertou:
        return {"mensagem": "✅ Resposta correta! +10 pontos"}
    else:
        return {"mensagem": f"❌ Resposta incorreta. A correta era '{pergunta['resposta_correta']}'"}
