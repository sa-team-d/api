from fastapi import HTTPException, Request
from src.config.db_config import SyncDatabase
from pymongo.collection import Collection
from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

import logging
import asyncio

logger = logging.getLogger("uvicorn-error")


def check_db(request, version: str):
    mongodb_obj = getattr(request.app, f"mongodb_{version}_obj")

    if isinstance(mongodb_obj, SyncDatabase):
        response = mongodb_obj.check_mongodb_connection()
    else:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(mongodb_obj.check_mongodb_connection())

    if response["status"] == "ok":
        return response
    else:
        raise HTTPException(status_code=500, detail=response)
    

def get_collection(
    request: Optional[Request] = None,
    any_collection: Optional[Collection[Any]] = None,
    version_db: Optional[str] = None,
    name: Optional[str] = None
) -> AsyncIOMotorCollection:
    """Get MongoDB collection either from request or direct collection reference.

    Args:
        request: FastAPI request object containing MongoDB client
        any_collection: Direct collection reference
        version_db: Database version string for MongoDB client
        name: Collection name

    Returns:
        AsyncIOMotorCollection: MongoDB collection

    Raises:
        ValueError: If invalid parameters are provided
    """
    if request is None and any_collection is None:
        raise ValueError("Must provide either request or collection reference")

    if request is None and any_collection is not None:
        return any_collection

    if not (name and version_db):
        raise ValueError("Must provide both name and version_db when using request")

    try:
        mongodb: AsyncIOMotorDatabase = getattr(request.app, f"mongodb_{version_db}")
        collection = mongodb.get_collection(name)
        return collection
    except Exception as e:
        raise ValueError(f"Error getting collection: {e}")