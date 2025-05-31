# admin_service/schemas/admin_schema.py

from pydantic import BaseModel

class AdminCreate(BaseModel):
    username: str
    password: str

class AdminOut(BaseModel):
    id: int
    username: str
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str  # "bearer"

class TokenData(BaseModel):
    username: str | None = None
