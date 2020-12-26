from pydantic import EmailStr, BaseModel
from typing import Optional
from datetime import datetime

class UserLoginSchema(BaseModel):
    username: str
    password: str

    class Config:
        orm_mode = True

class UserRegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    is_active: bool
    is_admin: bool
    is_superuser: bool = False

    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    email: EmailStr
    is_active: bool
    is_admin: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        orm_mode = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True

class LoginsLogsSchema(BaseModel):
    user_id: int = None
    client_host: str = None
    status: str

    class Config:
        orm_mode = True
