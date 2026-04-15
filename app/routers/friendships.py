from fastapi import APIRouter, Depends, Path
from fastapi.exceptions import HTTPException
from ..routers.user import get_current_user
from fastapi.responses import JSONResponse
from sqlalchemy import or_, and_

from sqlmodel import select

from typing import Annotated

from ..models.user import *

from ..routers.user import credentials_exception
from ..database import SessionDep

from ..models.friendships import *

router = APIRouter(tags=["friendships"])

@router.post("/add_friend/{phone}")
def add_friend(current_user: Annotated[UserDb, Depends(get_current_user)], phone: Annotated[str, Path()], session: SessionDep):    
    receiver = session.exec(select(UserDb).where(UserDb.phone == phone)).first()

    if not receiver:
        raise HTTPException(detail="Usuário não encontrado!", status_code=404)
    
    if receiver.id == current_user.id:
        raise HTTPException(detail="Você não pode enviar um pedido de amizade para si mesmo.", status_code=400)
   
    friend_request = Friendship(requester_id=current_user.id, receiver_id=receiver.id)

    session.add(friend_request)
    session.commit()
    session.refresh(friend_request)

    return JSONResponse(content={"message": "Pedido de amizade enviado com sucesso!"}, status_code=200)

@router.get("/friendships")
def list_friendships(
    current_user: Annotated[UserDb, Depends(get_current_user)],
    session: SessionDep
):
    friendships = session.exec(select(Friendship).where(
        and_(
            Friendship.status == "Accepted",
            Friendship.is_deleted == False
        ),
        or_(
            Friendship.requester_id == current_user.id,
            Friendship.receiver_id == current_user.id
        )
    )).all()

    return friendships


@router.delete("/delete_friendship/{user_id}")
def delete_friendship(current_user: Annotated[UserDb, Depends(get_current_user)], user_id: Annotated[int, Path()], session: SessionDep):
    user = session.exec(select(UserDb).where(UserDb.id == user_id)).first()

    if not user:
        raise HTTPException(detail="Usuário não encontrado!", status_code=404)
    

    friendship = session.exec(select(Friendship).where(
        or_(
            and_(
                Friendship.requester_id == user.id,
                Friendship.receiver_id == current_user.id
            ),
            and_(
                Friendship.requester_id == current_user.id,
                Friendship.receiver_id == user.id
            )
        )
    )).first()

    if friendship.receiver_id != current_user.id and friendship.requester_id != current_user.id:
        raise HTTPException(detail="Você não tem permissão para fazer essa chamada.", status_code=401)

    if not friendship or friendship.is_deleted:
        raise HTTPException(detail="Amizade não encontrada!", status_code=404)
    
    friendship.is_deleted = True

    session.add(friendship)
    session.commit()
    session.refresh(friendship)

    return JSONResponse(content={"message": "Amizade deletada com sucesso!"}, status_code=200)

@router.post("/accept_friendhsip/{user_id}")
def accept_friendship(current_user: Annotated[UserDb, Depends(get_current_user)], user_id: Annotated[int, Path()], session: SessionDep):
    friendship_request = session.exec(select(Friendship).where(Friendship.receiver_id == current_user.id, Friendship.requester_id == user_id, Friendship.status == "Pending", Friendship.is_deleted == False)).one_or_none()

    if not friendship_request:
        return HTTPException(detail="Pedido de amizade não encontrado!", status_code=404)
    
    friendship_request.status = "Accepted"
    session.commit()
    session.refresh(friendship_request)

    return JSONResponse(content={"message": "Pedido de amizade aceito."}, status_code=200)