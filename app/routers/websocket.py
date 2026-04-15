from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi import APIRouter, Depends, Path

from ..models.user import *
from ..models.friendships import *

from ..routers.user import ALGORITHM, SECRET_KEY
import jwt
from jwt.exceptions import InvalidTokenError

from ..database import SessionDep
from sqlmodel import select
from sqlalchemy import or_, and_

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        self.active_connections[user_id].remove(websocket)

    async def send_personal_message(self, message: str, user_id: int):
        for ws in self.active_connections.get(user_id, []):
            await ws.send_text(message)

    async def send_to_user(self, message: str, user_id: int):
        for ws in self.active_connections.get(user_id, []):
            await ws.send_text(message)

def get_user_from_token(token: str, session: SessionDep):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["id"]
        if not user_id:
            return None
    except InvalidTokenError:
        return None
    
    user = session.exec(select(UserDb).where(UserDb.id == user_id)).first()

    return user

manager = ConnectionManager()

@router.websocket("/ws/{friend_id}")
async def websocket_endpoint(friend_id: int, session: SessionDep, websocket: WebSocket):
    
    user_friend = session.exec(select(UserDb).where(UserDb.id == friend_id)).first()

    if not user_friend:
        await websocket.close(code=1008)
        return

    token = websocket.cookies.get("access_token")

    if not token:
        await websocket.close(code=1008)
        return

    current_user = get_user_from_token(session=session, token=token)

    if not current_user:
        await websocket.close(code=1008)
        return
    

    friendship = session.exec(
        select(Friendship).where(
            and_(
                Friendship.status == "Accepted",
                Friendship.is_deleted == False,
                or_(
                    and_(
                        Friendship.requester_id == current_user.id,
                        Friendship.receiver_id == user_friend.id
                    ),
                    and_(
                        Friendship.requester_id == user_friend.id,
                        Friendship.receiver_id == current_user.id
                    )
                )
            )
        )
    ).first()

    if not friendship:
        await websocket.close(code=1008)
        return
    
    await manager.connect(websocket=websocket, user_id=current_user.id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(user_id=current_user.id, message=data)
            await manager.send_to_user(user_id=user_friend.id, message=data)
    except WebSocketDisconnect:
        manager.disconnect(websocket=websocket, user_id=current_user.id)