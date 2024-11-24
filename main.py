import sys, os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import HTTPException
from contextlib import asynccontextmanager
from fastapi.requests import Request

sys.path.append(os.path.abspath("."))
from src.plugins.machine import controller as machine_controller
from src.plugins.user import controller as user_controller
from src.plugins.kpi import controller as kpi_controller
from src.plugins.report import controller as report_controller
from utils import description
from src.config.firebase_config import initialize_firebase
from src.config.db_config import AsyncDatabase, SyncDatabase
from src.utils  import check_db

import logging
from dotenv import load_dotenv
load_dotenv()

logger = logger = logging.getLogger('uvicorn.error')


initialize_firebase()

@asynccontextmanager
async def startup_shutdown_db(app: FastAPI):

    # sync_db_obj_g8 = SyncDatabase("DATABASE_URL_G8", "DATABASE_NAME_G8")
    # app.mongodb_g8 = sync_db_obj_g8.get_db()
    # app.mongodb_g8_obj = sync_db_obj_g8
    
    async_db_obj_g8 = AsyncDatabase("DATABASE_URL_G8", "DATABASE_NAME_G8")
    app.mongodb_g8 = async_db_obj_g8.get_db()
    app.mongodb_g8_obj = async_db_obj_g8

    # sync_db_obj_g2 = SyncDatabase("DATABASE_URL_G2", "DATABASE_NAME_G2")
    # app.mongodb_g2 = sync_db_obj_g2.get_db()
    # app.mongodb_g2_obj = sync_db_obj_g2

    async_db_obj_g2 = AsyncDatabase("DATABASE_URL_G2", "DATABASE_NAME_G2")
    app.mongodb_g2 = async_db_obj_g2.get_db()
    app.mongodb_g2_obj = async_db_obj_g2


    yield

    # sync_db_obj_g8.client.close()
    # sync_db_obj_g2.client.close()

    async_db_obj_g8.client.close()
    async_db_obj_g2.client.close()

API_VERSION = os.getenv("VERSION")

app = FastAPI(
    title="Industry 5.0 RESTful API",
    description=description,
    version=API_VERSION,
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc",
    lifespan=startup_shutdown_db
)

# CORS settings for local development
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")

@app.get("/docs", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")

@app.get("/redoc", summary="Redirect to ReDoc docs")
async def redirect_to_redoc():
    return RedirectResponse(url=f"/api/{API_VERSION}/redoc")

@app.get("/health/mongodb", summary="Check MongoDB connection")
async def check_mongodb_connection(request: Request, version: str = "g8"):
    if version != "g8" and version != "g2":
        raise HTTPException(status_code=400, detail="Invalid version")
    
    return check_db(request, version)

    

@app.get(
        "/mongodb/list_all_data", 
        summary="List all data in MongoDB",
        response_class=HTMLResponse,
        # include_in_schema=False
    
    )
async def list_all_data(request: Request, version: str = "g8"):
    if version != "g8" and version != "g2":
        raise HTTPException(status_code=400, detail="Invalid version")
    mongodb_obj = getattr(request.app, f"mongodb_{version}_obj")
    return await mongodb_obj.list_all_data()

router = APIRouter(prefix=f"/api/{API_VERSION}", tags=["API"])

app.include_router(router)
app.include_router(machine_controller.router)
app.include_router(user_controller.router)
app.include_router(kpi_controller.router)
app.include_router(report_controller.router)