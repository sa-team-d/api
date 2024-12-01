
import os
import motor.motor_asyncio
import json

from pprint import pprint
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv(dotenv_path=".env")


    

class DatabaseMixin:
    def get_db(self):
        return self.db

    def close_db(self):
        self.client.close()

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def get_all_databases(self):
        return self.client.list_database_names()

    def get_html_style(self) -> str:
        html = '''
        <style>
            :root {
                --primary: #2c3e50;
                --secondary: #34495e;
                --accent: #3498db;
                --bg-light: #f8f9fa;
            }
            .container { 
                font-family: 'Segoe UI', Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto;
                padding: 20px;
            }
            .collection { 
                margin: 25px 0; 
                background: var(--bg-light); 
                border-radius: 12px; 
                padding: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .collection-header { 
                background: var(--primary); 
                color: white; 
                padding: 15px 20px;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            .collection-stats {
                font-size: 0.9em;
                color: #ecf0f1;
            }
            .document { 
                background: white; 
                margin: 12px 0; 
                padding: 20px;
                border-radius: 8px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border: 1px solid #e9ecef;
            }
            .document:hover {
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .json { 
                font-family: 'Consolas', monospace; 
                white-space: pre-wrap;
                font-size: 14px;
                line-height: 1.5;
            }
            .empty { 
                color: #6c757d; 
                font-style: italic;
                padding: 20px;
                text-align: center;
            }
            .ref-id {
                color: var(--accent);
                font-size: 0.85em;
                margin-bottom: 5px;
            }
            .doc-header {
                border-bottom: 1px solid #eee;
                margin-bottom: 10px;
                padding-bottom: 5px;
            }
        </style>
        <div class="container">
        '''
        
        return html
    
class Database:
    def __init__(self, DATABASE_URL_ENV, DATABASE_NAME_ENV):
        self.DATABASE_URL = os.getenv(DATABASE_URL_ENV)
        self.DATABASE_NAME = os.getenv(DATABASE_NAME_ENV)

        if not self.DATABASE_URL:
            raise ValueError("Database URL is not set")
        if not self.DATABASE_NAME:
            raise ValueError("Database name is not set")
    

class AsyncDatabase(DatabaseMixin, Database):
    def __init__(self, DATABASE_URL_ENV, DATABASE_NAME_ENV):
        super().__init__(DATABASE_URL_ENV, DATABASE_NAME_ENV)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(self.DATABASE_URL)
        self.db = self.client[self.DATABASE_NAME]

    async def check_mongodb_connection(self):
        try:
            await self.client.admin.command("ismaster")
            all_databases = await self.get_all_databases()
            return {"status": "ok", "databases": all_databases}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def list_all_data(self):
        html = self.get_html_style()
        collections = await self.db.list_collection_names()
        for collection_name in collections:
            doc_count = await self.db[collection_name].count_documents({})
            
            html += f'''
            <div class="collection">
                <div class="collection-header">
                    <div>Collection: {collection_name}</div>
                    <div class="collection-stats">
                        Documents: {doc_count} | ID: {collection_name.lower().replace(" ", "_")}
                    </div>
                </div>
            '''
            
            documents = await self.db[collection_name].find({}).to_list(None)
            if documents:
                for doc in documents:
                    doc_id = str(doc['_id'])
                    # Extract a title field if exists, otherwise use ID
                    doc_title = doc.get('name', doc.get('title', f'Document {doc_id[:8]}...'))
                    
                    # Convert ObjectId to string for JSON serialization
                    doc['_id'] = doc_id
                    json_str = json.dumps(doc, indent=2, default=str)
                    json_str = json_str.replace('<', '&lt;').replace('>', '&gt;')
                    
                    html += f'''
                    <div class="document">
                        <div class="doc-header">
                            <div class="ref-id">Reference ID: {doc_id}</div>
                            <strong>{doc_title}</strong>
                        </div>
                        <div class="json">{json_str}</div>
                    </div>
                    '''
            else:
                html += '<div class="empty">No documents found in this collection</div>'
            
            html += '</div>'
        
        html += '</div>'
        return html

class SyncDatabase(DatabaseMixin, Database):
    def __init__(self, DATABASE_URL_ENV, DATABASE_NAME_ENV):
        super().__init__(DATABASE_URL_ENV, DATABASE_NAME_ENV)

        self.client = MongoClient(self.DATABASE_URL)
        self.db = self.client[self.DATABASE_NAME]
    

    def check_mongodb_connection(self):
        try:
            self.client.admin.command("ismaster")
            return {"status": "ok", "databases": self.get_all_databases()}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        

    async def list_all_data(self):
        html = self.get_html_style()

        for collection_name in self.db.list_collection_names():
            doc_count = self.db[collection_name].count_documents({})
            
            html += f'''
            <div class="collection">
                <div class="collection-header">
                    <div>Collection: {collection_name}</div>
                    <div class="collection-stats">
                        Documents: {doc_count} | ID: {collection_name.lower().replace(" ", "_")}
                    </div>
                </div>
            '''
            
            documents = list(self.db[collection_name].find({}))
            if documents:
                for doc in documents:
                    doc_id = str(doc['_id'])
                    # Extract a title field if exists, otherwise use ID
                    doc_title = doc.get('name', doc.get('title', f'Document {doc_id[:8]}...'))
                    
                    # Convert ObjectId to string for JSON serialization
                    doc['_id'] = doc_id
                    json_str = json.dumps(doc, indent=2, default=str)
                    json_str = json_str.replace('<', '&lt;').replace('>', '&gt;')
                    
                    html += f'''
                    <div class="document">
                        <div class="doc-header">
                            <div class="ref-id">Reference ID: {doc_id}</div>
                            <strong>{doc_title}</strong>
                        </div>
                        <div class="json">{json_str}</div>
                    </div>
                    '''
            else:
                html += '<div class="empty">No documents found in this collection</div>'
            
            html += '</div>'
        
        html += '</div>'
        return html

# Ogni volta che si importa db_config.py, si crea una nuova connessione al database, e non si chiude .
# import os
# from dotenv import load_dotenv
# from pymongo import MongoClient, errors

# load_dotenv()

# database_url = os.getenv("DATABASE_URL")
# database_name = os.getenv("DATABASE")
# debug_mode = os.getenv("DEBUG")

# try :
#     client = MongoClient(database_url)
#     db = client[database_name]
#     print("Connected to MongoDB")
# except errors.ConnectionFailure as e:
#     print(f"Error connecting to MongoDB: {e}")

# # check db connection
# if debug_mode: print(db.list_collection_names())

# machines_collection = db['machines']
# kpis_collection = db['kpis']

# try:
#     kpis_collection.create_index("name", unique=True)
#     machines_collection.create_index("name", unique=True)
# except errors.OperationFailure as e:
#     print(f"Error creating index: {e}")
# except errors.PyMongoError as e:
#     print(f"General MongoDB error: {e}")