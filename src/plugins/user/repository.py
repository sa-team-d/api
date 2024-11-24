from fastapi import HTTPException, Request
from pymongo.collection import Collection
from datetime import datetime, timezone

from src.plugins.user.schema import User
from src.utils import get_collection
from src.custom_exceptions import  UserNotFoundException

# mock a user database for now
users = {
    "k8SM6PwrJ4g663v5uZo8gfC7iND2": User(
        uid="k8SM6PwrJ4g663v5uZo8gfC7iND2",
        site= 0,
        name="Giovanni Bianchi",
        phone_number="1234567890",
        email="smo@example.com",
    ),
    "xM2kea8akaOKvYta26NMFBy8YnJ3": User(
        uid="xM2kea8akaOKvYta26NMFBy8YnJ3",
        name="Mario Rossi",
        site= 1,
        phone_number="0987654321",
        email="ffm@example.com",
    )
}

async def get_user_by_uid(uid: str, request: Request | None = None, user_collection: Collection[User]| None = None):

    # get collection
    user_collection = get_collection(request=request,  version_db="g8", name="users")

    # get user
    user = await user_collection.find_one({"uid": uid})

    if user is not None:
        return User(**user)
    else:
        raise UserNotFoundException("User not found")


async def get_user_by_email(email: str, request: Request | None = None, user_collection: Collection[User]| None = None):
    user_collection = get_collection(request=request,  version_db="g8", name="users")

    print(f"email: {email}")
    cursor = user_collection.find({"email": email})
    users = [User(**user) async for user in cursor]

    if users is None or len(users) == 0:
        raise UserNotFoundException(f"No user found by email {email}")
    
    return users

async def get_user_by_name(first_name: str, last_name: str, request: Request | None = None, user_collection: Collection[User]| None = None):
    
    user_collection = get_collection(request=request,  version_db="g8", name="users")

    # get users
    cursor = user_collection.find({"name": first_name.strip().title() + " " + last_name.strip().title()})
    users = [User(**user) async for user in cursor]
    
    if users is None or len(users) == 0:
        raise UserNotFoundException(f"No users found by name {first_name} {last_name}")
    return users 
    

async def update_user_db(uid: str, first_name: str = None, last_name: str = None, phone_number: str = None):
    if uid not in users:
        raise HTTPException(status_code=404, detail="User not found")
    user = users[uid]
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if phone_number:
        user.phone_number = phone_number
    user.updated_at = datetime.now(timezone.utc)
    return user

async def get_all_users(request: Request | None = None, user_collection: Collection[User]| None = None):
    # get collection
    user_collection = get_collection(request=request,  version_db="g8", name="users")

    # get all users
    users = user_collection.find()
    if users is None:
        raise UserNotFoundException("No users found")
    return [User(**user) async for user in users]
    