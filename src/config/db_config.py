import os
from dotenv import load_dotenv
from pymongo import MongoClient, errors

load_dotenv()

database_url = 'mongodb+srv://mmattiello2:phXQ49wnP17nthPp@cluster0.qr2kp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0' #os.getenv("DATABASE_URL")
database_name = 'smart_app'
debug_mode = True #os.getenv("DEBUG")

try :
    client = MongoClient(database_url)
    db = client[database_name]
    print("Connected to MongoDB")
except errors.ConnectionFailure as e:
    print(f"Error connecting to MongoDB: {e}")

# check db connection
if debug_mode: print(db.list_collection_names())

machines_collection = db['machines']
kpis_collection = db['kpis']

try:
    kpis_collection.create_index("name", unique=True)
    machines_collection.create_index("name", unique=True)
except errors.OperationFailure as e:
    print(f"Error creating index: {e}")
except errors.PyMongoError as e:
    print(f"General MongoDB error: {e}")