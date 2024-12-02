"""
User controller module.
Contains all the routes for user management.
"""
from fastapi import APIRouter, Depends, Request


from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.auth.auth_utils import get_uid_and_token
from .schema import User, UserResponse, UserLogin, UserWithToken
from . import repository as repo

import os
API_VERSION = os.getenv("VERSION")

router = APIRouter(prefix=f"/api/{API_VERSION}/user", tags=["User"])

# Endpoint to authenticate users and get their ID token (for testing purposes): we won't need this, frontend will handle this
@router.post("/login", response_model=UserResponse, status_code=200, summary="TEST ONLY: Simulate frontend login", description="Authenticate user and get firebase ID token")
async def login(request: Request, credentials: UserLogin):
    try:
        email = credentials.email
        password = credentials.password

        token,uid = get_uid_and_token(email, password)
        user = await repo.get_user_by_uid(uid, request=request)
        user_with_token  = UserWithToken(**user.model_dump(by_alias=True), id_token=token)
        return UserResponse(success=True, data=user_with_token, message="User authenticated successfully")
    except Exception as e:
        return UserResponse(success=False, data=None, message=str(e))

# Create a new user
@router.post("/", status_code=201, response_model=User, summary="Create a new user")
async def create_user(name:str, phone_number:str, email:str, site:str, user = Depends(verify_firebase_token_and_role)):
    return UserResponse(success=False, data=None, message="Not implemented")

# delete a user
@router.delete("/{user_id}", status_code=204, summary="Delete a user")
async def delete_user(user_id: str, user = Depends(verify_firebase_token_and_role)):
    return UserResponse(success=False, data=None, message="Not implemented")

# update user info
@router.put("/{user_id}", status_code=200, response_model=User, summary="Update user info")
async def update_user(user_id: str, name:str, phone_number:str, email:str, site:str, user = Depends(verify_firebase_token_and_role)):
    return UserResponse(success=False, data=None, message="Not implemented")

# list all users
@router.get("/list",status_code=200, response_model=UserResponse, summary="List all users")
async def list_users(request: Request, user = Depends(verify_firebase_token)):
    try:
        users = await repo.get_all_users(request)
        return UserResponse(success=True, data=users, message="Users listed successfully")
    except Exception as e:
        return UserResponse(success=False, data=None, message=str(e))

# show currrent user info
@router.get("/", status_code=200, response_model=UserResponse, summary="Get current user")
async def get_current_user(request: Request, user = Depends(verify_firebase_token)):
    try:
        u = await repo.get_user_by_uid(user.uid, request=request)
        return UserResponse(success=True, data=u, message="User retrieved successfully")
    except Exception as e:
        return UserResponse(success=False, data=None, message=str(e))

# filter users by name or email
@router.get("/filter", status_code=200, response_model=UserResponse, summary="Filter users by name or email")
async def filter_users(request: Request, first_name: str = None, last_name: str = None, email: str = None, user = Depends(verify_firebase_token)):
    try:
        if first_name and last_name:
            users = await repo.get_user_by_name(first_name, last_name, request=request)
        if email:
            users = await repo.get_user_by_email(email, request=request)
        return UserResponse(success=True, data=users, message="Users filtered successfully")
    except Exception as e:
        return UserResponse(success=False, data=None, message=str(e))\

@router.get("/:uid", status_code=200, response_model=UserResponse, summary="Get user by ID")
async def get_user_by_id(request: Request, uid: str, user = Depends(verify_firebase_token)):
    try:
        u = await repo.get_user_by_uid(uid, request=request)
        return UserResponse(success=True, data=u, message="User retrieved successfully")
    except Exception as e:
        return UserResponse(success=False, data=None, message=str(e))