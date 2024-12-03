import logging
import os

from fastapi import Request

from pymongo.collection import Collection
from typing import Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection

from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")




DATABASE_NAME = os.getenv("DATABASE_NAME")

logger = logging.getLogger("uvicorn-error")


async def create_report_collection(request: Request = None, mongodb: AsyncIOMotorDatabase = None ) -> None:
    
    if request is None and mongodb is None:
        raise ValueError("Must provide either request or mongodb")
    

    if request is not None:    
        # Connect to MongoDB
        db: AsyncIOMotorDatabase = request.app.mongodb
    else:
        db = mongodb
        
    # Define validator schema
    
    validator = {
    '$jsonSchema': {
        'bsonType': 'object',
        'required': ['kpi_name', 'name', 'start_date', 'end_date', 'user_uid', 'sites_id', 'url'],
        'properties': {
            'kpi_name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'start_date': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'end_date': {
                'bsonType': 'date',
                'description': 'must be a date and is required'
            },
            'user_uid': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'sites_id': {
                'bsonType': 'array',
                'items': {
                    'bsonType': 'objectId'
                },
                'description': 'must be an array of ObjectId and is required',
            },
            'url': {
                'bsonType': 'string',
                'description': 'must be a string and is required',
            }
        }
    }
}

    # Create collection with validator
    try:
        await db.create_collection('reports', validator=validator)
        print("Reports collection created with validator")
    except Exception as e:
        print(f"Collection already exists: {e}")
        # Update validator if collection exists
        await db.command('collMod', 'reports', validator=validator)
        print("Updated validator for existing collection")
    return db['reports']


async def create_user_collection(request: Request):
    # Get MongoDB client from request
    db = request.app.mongodb

    # Define validator schema
    validator = {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': ['uid', 'email', 'first_name', 'last_name', 'phone_number'],
            'properties': {
                'uid': {
                    'bsonType': 'string',
                    'description': 'Firebase user ID - must be a string and is required'
                },
                'email': {
                    'bsonType': 'string',
                    'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
                    'description': 'must be a valid email string and is required'
                },
                'site': {
                    'bsonType': ['int', 'null'],
                    'description': 'must be an integer or null'
                },
                'first_name': {
                    'bsonType': 'string',
                    'description': 'must be a string and is required'
                },
                'last_name': {
                    'bsonType': 'string', 
                    'description': 'must be a string and is required'
                },
                'phone_number': {
                    'bsonType': 'string',
                    'description': 'must be a string and is required'
                }
            }
        }
    }

    # Create or update collection with validator
    try:
        await db.create_collection('users', validator=validator)
        print("Users collection created with validator")
    except Exception as e:
        print(f"Collection exists, updating validator: {e}")
        await db.command('collMod', 'users', validator=validator)
        print("Updated validator for existing collection")

    # Create index on email field
    await db['users'].create_index('email', unique=True)
    await db['users'].create_index('uid', unique=True)
    return db['users']

def get_collection(
    request: Optional[Request] = None,
    any_collection: Optional[Collection[Any]] = None,
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

    if name is None and request.app.mongodb is None:
        raise ValueError("Must provide both name and mongodb when using request")

    try:
        collection = request.app.mongodb.get_collection(name)
        return collection
    except Exception as e:
        raise ValueError(f"Error getting collection: {e}")