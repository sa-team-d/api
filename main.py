import sys, os
from turtle import dot
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import desc

sys.path.append(os.path.abspath("."))
from src.plugins.machine import controller as machine_controller
from src.plugins.user import controller as user_controller
from src.plugins.kpi import controller as kpi_controller
from src.plugins.report import controller as report_controller
from utils import description
from src.config.firebase_config import initialize_firebase

import logging
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

initialize_firebase()

API_VERSION = os.getenv("VERSION")
app = FastAPI(
    title="Industry 5.0 RESTful API",
    description=description,
    version=API_VERSION,
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc",
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

router = APIRouter(prefix=f"/api/{API_VERSION}", tags=["API"])

app.include_router(router)
app.include_router(machine_controller.router)
app.include_router(user_controller.router)
app.include_router(kpi_controller.router)
app.include_router(report_controller.router)