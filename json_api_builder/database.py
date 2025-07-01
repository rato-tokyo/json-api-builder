"""
Database setup for the JSON API Builder.
"""

import contextlib
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class Database:
    """Handles database connections and sessions."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextlib.contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Generator function to get a database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self) -> None:
        """Creates all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def get_db_file_path(self) -> str:
        """Returns the path to the database file."""
        url_str = str(self.engine.url)
        if url_str.startswith("sqlite:///"):
            return url_str[10:]
        raise ValueError("Database path could not be determined from engine URL.")
