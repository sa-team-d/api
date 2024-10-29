from fastapi import FastAPI
from src.plugins.machine import controller

app = FastAPI()

# Include routers
app.include_router(controller.router)
