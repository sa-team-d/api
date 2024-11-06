from fastapi import Depends, HTTPException
from fastapi import security
from firebase_admin import auth
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify the Firebase token and return the decoded token
    """
    try:
        print(f"Received token: {credentials.credentials}")
        decoded_token = auth.verify_id_token(credentials.credentials)
        print(f"Decoded token: {decoded_token}")
        # Verify the token with Firebase Admin
        auth.verify_id_token(credentials.credentials)
        return decoded_token
    except Exception as e:
        print(f"Error verifying token: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase token") from e

def verify_firebase_token_and_role(required_role: str):
    """
    Verify the Firebase token and check if the user has the required role
    """
    def role_verifier(credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            print(f"Received token: {credentials.credentials}")
            decoded_token = auth.verify_id_token(credentials.credentials)
            print(f"Decoded token: {decoded_token}")
            # Verify the token with Firebase Admin
            auth.verify_id_token(credentials.credentials)
            # Check if user has the required role
            user_role = decoded_token.get("role")
            if user_role != required_role:
                raise HTTPException(status_code=403, detail=f"Insufficient permissions. Required role: {required_role}")
            elif required_role == "USER":
                print(f"User is a valid user")
            else:
                print(f"User has the required role: {required_role}")
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            raise HTTPException(status_code=401, detail="Invalid Firebase token") from e
    return role_verifier

#async def get_current_user(token: str = Security(security)) -> User:
#    """
#    Get the current user from the Firebase token
#    Args:
#        token (str): Firebase token
#    Returns:
#        User: The current user
#    """
#    try:
#        decoded_token = auth.verify_id_token(token)
#        uid = decoded_token["uid"]
#        print(uid)
#        firebase_user = auth.get_user(uid)
#        return User(
#            id=firebase_user.uid,
#            email=firebase_user.email,
#            display_name=firebase_user.display_name,
#            # Add other fields as necessary
#        )
#    except Exception as e:
#        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
#
#async def check_permissions(user: User, required_permissions: list):
#    # Assuming `user.permissions` is a list of permissions the user has
#    if not set(required_permissions).issubset(set(user.permissions)):
#        raise HTTPException(status_code=403, detail="Insufficient permissions")
#
#async def get_admin_user(token: str = Security(security)) -> User:
#    try:
#        decoded_token = auth.verify_id_token(token)
#        uid = decoded_token["uid"]
#        firebase_user = auth.get_user(uid)
#        user = User(
#            id=firebase_user.uid,
#            email=firebase_user.email,
#            display_name=firebase_user.display_name,
#            # Add other fields as necessary
#        )
#        if "admin" not in user.permissions:
#            raise HTTPException(status_code=403, detail="Admin permissions required")
#        return user
#    except Exception as e:
#        raise HTTPException(status_code=401, detail="Invalid authentication credentials")