from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel):
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)
    password: str = Field(min_length=6, max_length=12)

class UserDb(SQLModel, table=True):
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)
    hashed_password: str
    is_deleted: bool = Field(default=False)
    created_at: str

class UserPublic(SQLModel):
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)