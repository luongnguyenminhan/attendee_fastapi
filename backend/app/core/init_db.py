from sqlmodel import SQLModel, create_engine

from app.core.config import settings

# Import all models to ensure they are registered with SQLModel.metadata

engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
