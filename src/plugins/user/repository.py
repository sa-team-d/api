from os import name
from typing import List, Dict, Optional
from fastapi import HTTPException
from datetime import datetime, timezone
from src.models import User

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

async def get_user(uid: str):
    if uid not in users:
        raise HTTPException(status_code=404, detail="User not found")
    return users[uid]

async def get_user_by_email(email: str):
    us = []
    for user in users.values():
        if user.email == email:
            us.append(user)
    if len(us) > 0:
        return us
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def get_user_by_name(first_name: str, last_name: str):
    us = []
    for user in users.values():
        if user.first_name == first_name and user.last_name == last_name:
            us.append(user)
    if len(us) > 0:
        return us
    else:
        raise HTTPException(status_code=404, detail="User not found")

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

async def get_all_users():
    return list(users.values())

#class UserRepository(BaseRepository):
#    async def create_user(self, user: User) -> User:
#        if user.uid in self.users:
#            raise HTTPException(status_code=400, detail="User already exists")
#        user.created_at = datetime.now(timezone.utc)
#        self.users[user.uid] = user
#        return user
#
#    async def get_user(self, user_id: str) -> User:
#        if user_id not in self.users:
#            raise HTTPException(status_code=404, detail="User not found")
#        return self.users[user_id]
#
#    async def get_user_by_email(self, email: str) -> User:
#        for user in self.users.values():
#            if user.email == email:
#                return user
#        raise HTTPException(status_code=404, detail="User not found")
#
#    async def list_users(self, page: int = 1, per_page: int = 20,
#                        filters: Optional[Dict] = None) -> Dict:
#        users = list(self.users.values())
#        if filters:
#            for key, value in filters.items():
#                users = [u for u in users if getattr(u, key, None) == value]
#        return await self.paginate(users, page, per_page)
#
#    async def update_user(self, user_id: str, user_data: Dict) -> User:
#        if user_id not in self.users:
#            raise HTTPException(status_code=404, detail="User not found")
#        user = self.users[user_id]
#        for key, value in user_data.items():
#            setattr(user, key, value)
#        user.updated_at = datetime.utcnow()
#        return user
#
#    async def delete_user(self, user_id: str) -> None:
#        if user_id not in self.users:
#            raise HTTPException(status_code=404, detail="User not found")
#        del self.users[user_id]
#
#    async def update_user_roles(self, user_id: str, roles: List[str]) -> User:
#        user = await self.get_user(user_id)
#        user.roles = roles
#        user.updated_at = datetime.now(timezone.utc)
#        return user
#
#    async def verify_user_email(self, user_id: str) -> User:
#        user = await self.get_user(user_id)
#        user.is_verified = True
#        user.updated_at = datetime.now(timezone.utc)
#        return user
#
#    async def disable_user(self, user_id: str) -> User:
#        user = await self.get_user(user_id)
#        user.is_active = False
#        user.updated_at = datetime.now(timezone.utc)
#        return user
#
#    async def enable_user(self, user_id: str) -> User:
#        user = await self.get_user(user_id)
#        user.is_active = True
#        user.updated_at = datetime.now(timezone.utc)
#        return user
#
#
#    async def list_user_roles(self) -> List[UserRole]:
#        user_roles = []
#        for user in self.users.values():
#            user_roles.append(UserRole(user_id=user.uid, roles=user.roles))
#        return user_roles