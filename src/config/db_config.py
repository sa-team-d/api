import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

database_url = os.getenv("DATABASE_URL")
debug_mode = os.getenv("DEBUG")

client = MongoClient(database_url)
db = client['smart_app']
machines_collection = db['machines']
kpis_collection = db['kpis']

try:
    kpis_collection.create_index("name", unique=True)
except errors.OperationFailure as e:
    print(f"Error creating index: {e}")
except errors.PyMongoError as e:
    print(f"General MongoDB error: {e}")