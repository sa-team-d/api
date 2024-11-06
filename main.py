import sys, os
from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import RedirectResponse

sys.path.append(os.path.abspath("."))
from src.plugins.machine import controller as machine_controller
from src.plugins.user import controller as user_controller

from src.plugins.auth.firebase import verify_firebase_token_and_role
from src.plugins.auth.auth_utils import get_id_token
from src.plugins.auth.firebase_config import initialize_firebase

import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

initialize_firebase()

app = FastAPI(
    title="Industry 5.0 API"
)

router = APIRouter(prefix="/api/v1", tags=["API"])

@router.get("/", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(router)
app.include_router(machine_controller.router)
app.include_router(user_controller.router)

