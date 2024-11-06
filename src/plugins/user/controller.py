from fastapi import APIRouter, Depends
from httpx import get
from .schema import User
from .repository import add_user_to_db, get_all_users
from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.auth.auth_utils import get_id_token

router = APIRouter(prefix="/api/v1/user", tags=["User"])

# Endpoint to authenticate users and get their ID token (for testing purposes)
@router.post("/login")
async def login(email: str, password: str):
    """
    Authenticate the user and return the ID token
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

# Endpoint to list all users
@router.get("/list")
async def list_users(user = Depends(verify_firebase_token)):
    """
    List all users
    Returns:
        dict: List of all users
    """
    try:
        users = await get_all_users()
        for u in users:
            print(u)
        return {"users": users}
    except Exception as e:
        return {"error": str(e)}

####### Example routes with role-based access control #######

# Route accessible only by FFM role
@router.get("/ffm-only")
async def ffm_only(user=Depends(verify_firebase_token_and_role("FFM"))):
    return {"message": "Hello, FFM user!", "user": user}

# Route accessible only by SMO role
@router.get("/smo-only")
async def smo_only(user=Depends(verify_firebase_token_and_role("SMO"))):
    return {"message": "Hello, SMO user!", "user": user}

# Route accessible by all authenticated users
@router.get("/all-users")
async def all_users(user=Depends(verify_firebase_token_and_role("USER"))):
    return {"message": "Hello, authenticated user!", "user": user}

####################

## Auth endpoints
#@router.post("/auth/firebase/login", response_model=FirebaseAuthResponse)
#async def firebase_login(auth_request: FirebaseAuthRequest):
#    # Firebase auth logic here
#    pass
#
#@router.post("/auth/firebase/register", response_model=UserResponse)
#async def register_user(user: UserCreate, repo: UserRepository = Depends()):
#    return await repo.create_user(user)
#@router.post("/auth/firebase/verify-email")
#async def verify_email(
#    user: UserResponse = Depends(get_current_user),
#    repo: UserRepository = Depends()
#):
#    return await repo.verify_user_email(user.id)
## User endpoints
#@router.get("/users/me", response_model=UserResponse)
#async def get_current_user_profile(
#    user: UserResponse = Depends(get_current_user)
#):
#    return user
#
#@router.put("/users/me", response_model=UserResponse)
#async def update_current_user_profile(
#    user_update: UserUpdate,
#    current_user: UserResponse = Depends(get_current_user),
#    repo: UserRepository = Depends()
#):
#    return await repo.update_user(current_user.id, user_update)
#
#@router.get("/users/{user_id}", response_model=UserResponse)
#async def get_user(
#    user_id: str,
#    repo: UserRepository = Depends()
#):
#    return await repo.get_user(user_id)
#
#@router.get("/users", response_model=Dict)
#async def list_users(
#    page: int = Query(1, ge=1),
#    per_page: int = Query(20, ge=1, le=100),
#    filters: Optional[Dict] = None,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.list_users(page, per_page, filters)
#
#@router.put("/users/{user_id}", response_model=UserResponse)
#async def update_user(
#    user_id: str,
#    user_update: UserUpdate,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.update_user(user_id, user_update)
#
#@router.delete("/users/{user_id}")
#async def delete_user(
#    user_id: str,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    await repo.delete_user(user_id)
#    return {"message": "User deleted successfully"}
#
## Admin endpoints
#@router.post("/admin/users/disable")
#async def disable_user(
#    user_id: str,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.disable_user(user_id)
#
#@router.post("/admin/users/enable")
#async def enable_user(
#    user_id: str,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.enable_user(user_id)
#
#@router.post("/admin/users/roles", response_model=UserResponse)
#async def update_user_roles(
#    user_role: UserRole,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.update_user_roles(user_role.user_id, user_role.roles)
#
#@router.get("/admin/users/roles", response_model=List[UserRole])
#async def list_user_roles(
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.list_user_roles()
#
#@router.delete("/admin/users/roles")
#async def remove_user_roles(
#    user_id: str,
#    repo: UserRepository = Depends(),
#    _: UserResponse = Depends(get_admin_user)
#):
#    return await repo.update_user_roles(user_id, [])