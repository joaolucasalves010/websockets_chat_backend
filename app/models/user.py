from sqlmodel import SQLModel, Field
from datetime import datetime

import re

from pydantic import field_validator

class User(SQLModel):
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)
    password: str = Field(min_length=6, max_length=72)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned_v = re.sub(r"[\s\-\(\)]", "", v)
        if not cleaned_v.is_digit():
            raise ValueError("Telefone inválido.")
        return v


class UserDb(SQLModel, table=True):
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)
    hashed_password: str
    is_deleted: bool = Field(default=False)
    created_at: str

    __tablename__ = "users"

class UserPublic(SQLModel):
    id: int | None= Field(default=None, primary_key=True)
    username: str = Field(min_length=8, max_length=20)
    phone: str = Field(min_length=9, max_length=11)

class UserUpdate(SQLModel):
    username: str | None = Field(default=None, min_length=8, max_length=20)
    phone: str | None = Field(default=None, min_length=9, max_length=11)
    password: str | None = Field(default=None, min_length=6, max_length=72)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        cleaned_v = re.sub(r"[\s\-\(\)]", "", v)
        if not cleaned_v.is_digit():
            raise ValueError("Telefone inválido.")
        return v