"""
User controller module.
Contains all the routes for user management.
"""
from fastapi import APIRouter, Depends, HTTPException
from src.models import User
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.auth.auth_utils import get_id_token
from .repository import get_all_users, get_user, get_user_by_email, get_user_by_name

import os
API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/user", tags=["User"])

# Endpoint to authenticate users and get their ID token (for testing purposes): we won't need this, frontend will handle this
@router.post("/login", response_model=dict, status_code=200, summary="Authenticate user and get ID token")
async def login(email: str, password: str):
    """
    TEST ONLY: Authenticate user and get ID token
    Args:
        email (str): User email
        password (str): User password

    Returns:
        dict: ID token if successful, error message otherwise
    """
    try:
        token = get_id_token(email, password)
        return {"id_token": token}
    except Exception as e:
        return {"error": str(e)}

# list all users
@router.get("/list",status_code=200, response_model=list[User], summary="List all users")
async def list_users(user = Depends(verify_firebase_token)):
    try:
        users = await get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# show currrent user info
@router.get("/", status_code=200, response_model=User, summary="Get current user")
async def get_current_user(user = Depends(verify_firebase_token)):
    try:
        u = await get_user(user.get("uid"))
        return u
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# filter users by name or email
@router.post("/filter", status_code=200, response_model=list[User], summary="Filter users by name or email")
async def filter_users(first_name: str = None, last_name: str = None, email: str = None, user = Depends(verify_firebase_token)):
    try:
        if first_name and last_name:
            users = await get_user_by_name(first_name, last_name)
        if email:
            users = await get_user_by_email(email)
        users
    except Exception as e:
        HTTPException(status_code=404, detail=str(e))