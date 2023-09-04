from __future__ import annotations

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserRead, UserCreate

from operations.router import router as router_operation
from tasks.router import router as router_tasks
from pages.router import router as router_pages
from chat.router import router as router_chat

from redis import asyncio as aioredis

"""
    Чтобы создать приложение нужно импортировать класс FastAPI из библиотеки fastapi и
создать экземпляр класса FastAPI (параметр класса title - название проекта)
"""

app = FastAPI(title='Trading App')

"""
    Для создания эндпоинтов необходимо задекорировать функцию (Класс) декоратором 
    @app.[метод запроса]([название эндпоинта])
    Пример
    @app.get('/')
    def get_hello():
        return 'Hello world'

"""

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router_operation)
app.include_router(router_tasks)
app.include_router(router_pages)
app.include_router(router_chat)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding='utf-8', decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
