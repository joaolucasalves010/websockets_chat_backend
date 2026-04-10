from sqlmodel import Session, create_engine, SQLModel
from typing import Annotated

from fastapi import Depends

database = "database.db"
database_url = f"sqlite:///{database}"
engine = create_engine(database_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]