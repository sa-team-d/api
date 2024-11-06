from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
import sys, os

from jwt import decode
sys.path.append(os.path.abspath("."))
from src.plugins.machine import controller as machine_controller
from src.plugins.dashboard import controller as dashboard_controller
# from src.plugins.auth import controller as auth_controller
from src.plugins.report import controller as report_controller
from src.plugins.user import controller as user_controller

from fastapi import FastAPI, Depends
from src.plugins.auth.dependencies import verify_firebase_token_and_role
from src.plugins.auth.auth_utils import get_id_token
from src.plugins.auth import firebase_config

import os
from dotenv import load_dotenv

load_dotenv()

import  logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industry 5.0 API"

)

# Endpoint to authenticate users and get their ID token (for testing purposes)
@app.post("/login")
async def login(email: str, password: str):
    try:
        token = get_id_token(email, password)
        return {"id_token": token}
    except Exception as e:
        return {"error": str(e)}

# Route accessible only by FFM role
@app.get("/ffm-only")
async def ffm_only(user=Depends(verify_firebase_token_and_role("FFM"))):
    return {"message": "Hello, FFM user!", "user": user}

# Route accessible only by SMO role
@app.get("/smo-only")
async def smo_only(user=Depends(verify_firebase_token_and_role("SMO"))):
    return {"message": "Hello, SMO user!", "user": user}

router = APIRouter(prefix="/api/v1", tags=["API"])

@router.get("/", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(router)

app.include_router(machine_controller.router)

app.include_router(dashboard_controller.router)
# app.include_router(auth_controller.router)
app.include_router(report_controller.router)
app.include_router(user_controller.router)

