from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse

from src.plugins.machine import controller as machine_controller
from src.plugins.dashboard import controller as dashboard_controller
# from src.plugins.auth import controller as auth_controller
from src.plugins.report import controller as report_controller
from src.plugins.user import controller as user_controller
import  logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Industry 5.0 API"

)





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

