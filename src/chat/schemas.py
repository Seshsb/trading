from pydantic import BaseModel


class Like(BaseModel):
    id: int | str
    cnt: int | str


class ClientId(BaseModel):
    client_id: int | str