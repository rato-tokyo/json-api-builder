"""
SQLAlchemy models for the JSON API Builder.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base: Any = declarative_base()


class GenericTable(Base):
    """A generic table to store JSON data."""

    __tablename__ = "generic_data"

    id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(String(50), index=True, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
