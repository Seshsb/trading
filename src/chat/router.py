from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from typing import List
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from chat.models import Message
from chat.schemas import Like, ClientId
from database import async_session_maker, get_async_session

router = APIRouter(
    prefix='/chat',
    tags=['chat']
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, client_id, add_to_db: bool):
        if add_to_db:
            await self.add_messages_to_database(message, client_id)
        for connection in self.active_connections:
            await connection.send_text(message)

    @staticmethod
    async def add_messages_to_database(message: str, client_id: int):
        async with async_session_maker() as session:
            stmt = insert(Message).values(
                message=message,
                client_id=client_id
            )
            await session.execute(stmt)
            await session.commit()


manager = ConnectionManager()


@router.get('/last_messages')
async def get_last_messages(
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Message).order_by(Message.id.desc()).limit(5)
    messages = await session.execute(query)
    messages = messages.all()
    messages_list = [msg[0].as_dict() for msg in messages]
    return messages_list


@router.post('/post_likes')
async def post_likes(
        like: Like,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        query = update(Message).values(
            cnt_likes=like.dict().get('cnt')
        ).where(Message.client_id == like.dict().get('id'))
        await session.execute(query)
        await session.commit()

        return {'status': 'success'}
    except Exception:
        raise HTTPException(status_code=500, detail={
            'status': 'error',
            'data': None,
            'details': None
        })


@router.get('/get_likes/{client_id}')
async def get_likes(
        client_id: int | str,
        session: AsyncSession = Depends(get_async_session)
):
    try:
        query = select(Message).where(Message.client_id == client_id)
        result = await session.execute(query)
        return {
            "status": "success",
            "data": result.scalars().first(),
            "details": None
        }
    except Exception:
        raise HTTPException(status_code=500, detail={
            "status": "error",
            "data": None,
            "details": None
        })


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client #{client_id} says: {data}",
                                    client_id=client_id, add_to_db=True)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat",
                                client_id=client_id, add_to_db=False)
