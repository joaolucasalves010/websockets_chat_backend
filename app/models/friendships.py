from sqlmodel import SQLModel, Field
from datetime import datetime

from enum import Enum

class StatusEnum(str, Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    DECLINED = "Declined"

class Friendships(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="users.id")
    receiver_id: int = Field(foreign_key="users.id")
    status: StatusEnum = Field(default=StatusEnum.PENDING)
    is_deleted: bool = Field(default=False)