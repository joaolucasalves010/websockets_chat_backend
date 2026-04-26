from fastapi import APIRouter, Depends, UploadFile, File
from ..models.user import *

from fastapi.exceptions import HTTPException

from typing import Annotated
from pathlib import Path

from ..database import SessionDep

from fastapi.responses import JSONResponse

import os

from .user import get_current_user

ROOT_PATH = Path(__file__).parent.parent
IMAGE_DIR = os.path.join(ROOT_PATH, "uploads")

ALLOWED_EXTENSIONS = {".jpeg" , ".png", ".jpg"}

router = APIRouter(tags=["user avatar"])

@router.post("/users/avatar")
async def upload_avatar(current_user: Annotated[UserDb, Depends(get_current_user)], image: Annotated[UploadFile, File()], session: SessionDep):

    file_extension = Path(image.filename).suffix

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(detail="Formato de arquivo não permitido", status_code=400)
    
    if current_user.image_url is not None:
        os.remove(os.path.join(ROOT_PATH, current_user.image_url))
    
    with open(os.path.join(IMAGE_DIR, f"{current_user.phone}{file_extension}"), 'wb') as f:
        content = await image.read()
        f.write(content)

    current_user.image_url = f"uploads/{current_user.phone}{file_extension}"

    session.commit()
    session.refresh(current_user)
    return JSONResponse(content={"message": "Foto adicionada com sucesso."}, status_code=200)

@router.delete("/users/avatar")
def delete_avatar(current_user: Annotated[UserDb, Depends(get_current_user)], session: SessionDep):
    if current_user.image_url is None:
        return HTTPException(detail="Este usuário não possui imagem", status_code=404)
    
    os.remove(os.path.join(ROOT_PATH, current_user.image_url))
    current_user.image_url = None
    session.commit()
    session.refresh(current_user)
    
    return JSONResponse(content={"message": "Foto de usuário deletada com sucesso."}, status_code=200)