from fastapi import APIRouter, Body, Cookie
from typing import Annotated
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta
import os

import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from sqlmodel import select

from ..database import SessionDep

from ..models.user import *

from pwdlib import PasswordHash

router = APIRouter()

password_hash = PasswordHash.recommended()

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.environ["SECRET_KEY"]
EXPIRE_ACCESS_TOKEN = 30

def verify_password(password: str, user: UserDb):
    if not password_hash.verify(password, user.hashed_password):
        raise HTTPException(detail="Credenciais inválidas", status_code=400)


def authenticate_user(phone: str, password: str, session: SessionDep):
    user = session.exec(select(UserDb).where(UserDb.phone == phone)).first()
    if not user:
        raise HTTPException(detail="Usuário não encontrado", status_code=404)

    verify_password(password=password, user=user)

    return user

def create_access_token(user: UserDb):
    to_encode = {"id": user.id, "phone": user.phone, "username": user.username}
    to_encode.update({"exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_ACCESS_TOKEN)})
    return jwt.encode(user.model_dump(), SECRET_KEY, algorithm=ALGORITHM)

def verify_existing_user(phone: str, session: SessionDep):
    user = session.exec(select(UserDb).where(UserDb.phone == phone)).first()
    if user:
        raise HTTPException(detail="Já existe um usuário com esse número de telefone!", status_code=400)

@router.post("/users/create_user", response_model=UserPublic)
def create_user(
    user: Annotated[User, Body()],
    session: SessionDep
):
    verify_existing_user(phone=user.phone, session=session)

    now = datetime.now()
    user_db = UserDb(username=user.username, hashed_password=password_hash.hash(user.password), phone=user.phone, created_at=now.strftime("%d/%m/%Y"))
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db

@router.post("/login")
def login(phone: Annotated[str, Body()], password: Annotated[str, Body()], session: SessionDep, response: Response):
    user = authenticate_user(phone=phone, password=password, session=session)
    access_token = create_access_token(user)

    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return {"access_token": access_token}

@router.get("/users/me", response_model=UserPublic)
def get_current_user( session: SessionDep, access_token: str = Cookie()):
    credentials_exception = HTTPException(
        detail="Credenciais inválidas",
        status_code=401
    )

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["id"]
        if not user_id:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    
    user = session.exec(select(UserDb).where(UserDb.id == user_id)).first()

    return user