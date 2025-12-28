# backend/app/db/__init__.py
from .mongodb import MongoDB, get_database

__all__ = ["MongoDB", "get_database"]
