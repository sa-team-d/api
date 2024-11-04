from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth
from src.models import User
from fastapi import HTTPException
from src.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Security(oauth2_scheme)) -> User:
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
        firebase_user = auth.get_user(uid)
        return User(
            id=firebase_user.uid,
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            # Add other fields as necessary
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    

async def check_permissions(user: User, required_permissions: list):
    # Assuming `user.permissions` is a list of permissions the user has
    if not set(required_permissions).issubset(set(user.permissions)):
        raise HTTPException(status_code=403, detail="Insufficient permissions")





async def get_admin_user(token: str = Security(oauth2_scheme)) -> User:
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token["uid"]
        firebase_user = auth.get_user(uid)
        user = User(
            id=firebase_user.uid,
            email=firebase_user.email,
            display_name=firebase_user.display_name,
            # Add other fields as necessary
        )
        if "admin" not in user.permissions:
            raise HTTPException(status_code=403, detail="Admin permissions required")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")