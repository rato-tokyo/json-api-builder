"""
json-api-builder: A Python library to easily build FastAPI servers for storing JSON data.
"""

from .api_builder import APIBuilder
from .json_export import export_database_to_json
from .json_import import import_database_from_json
from .models import Base

__version__ = "0.2.0"  # Version bump for breaking changes
__all__ = [
    "APIBuilder",
    "export_database_to_json",
    "import_database_from_json",
    "Base",
]
