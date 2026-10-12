from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine
from core_api.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
