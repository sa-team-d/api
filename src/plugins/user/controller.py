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
@router.post("/login", response_model=dict, status_code=200, summary="TEST ONLY: Simulate frontend login", description="Authenticate user and get firebase ID token")
async def login(email: str, password: str):
    try:
        token = get_id_token(email, password)
        return {"id_token": token}
    except Exception as e:
        return {"error": str(e)}

# Create a new user
@router.post("/", status_code=201, response_model=User, summary="Create a new user")
async def create_user(name:str, phone_number:str, email:str, site:str, user = Depends(verify_firebase_token_and_role)):
    raise HTTPException(status_code=404, detail="Not implemented")

# delete a user
@router.delete("/{user_id}", status_code=204, summary="Delete a user")
async def delete_user(user_id: str, user = Depends(verify_firebase_token_and_role)):
    raise HTTPException(status_code=404, detail="Not implemented")

# update user info
@router.put("/{user_id}", status_code=200, response_model=User, summary="Update user info")
async def update_user(user_id: str, name:str, phone_number:str, email:str, site:str, user = Depends(verify_firebase_token_and_role)):
    raise HTTPException(status_code=404, detail="Not implemented")

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
@router.get("/filter", status_code=200, response_model=list[User], summary="Filter users by name or email")
async def filter_users(first_name: str = None, last_name: str = None, email: str = None, user = Depends(verify_firebase_token)):
    try:
        if first_name and last_name:
            users = await get_user_by_name(first_name, last_name)
        if email:
            users = await get_user_by_email(email)
        users
    except Exception as e:
        HTTPException(status_code=404, detail=str(e))