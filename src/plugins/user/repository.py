from typing import List, Dict, Optional
from fastapi import HTTPException
from src.models import User, UserRole
from src.repository import BaseRepository
from datetime import datetime, timezone


class UserRepository(BaseRepository):
    async def create_user(self, user: User) -> User:
        if user.uid in self.users:
            raise HTTPException(status_code=400, detail="User already exists")
        user.created_at = datetime.now(timezone.utc)
        self.users[user.uid] = user
        return user

    async def get_user(self, user_id: str) -> User:
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        return self.users[user_id]

    async def get_user_by_email(self, email: str) -> User:
        for user in self.users.values():
            if user.email == email:
                return user
        raise HTTPException(status_code=404, detail="User not found")

    async def list_users(self, page: int = 1, per_page: int = 20, 
                        filters: Optional[Dict] = None) -> Dict:
        users = list(self.users.values())
        if filters:
            for key, value in filters.items():
                users = [u for u in users if getattr(u, key, None) == value]
        return await self.paginate(users, page, per_page)

    async def update_user(self, user_id: str, user_data: Dict) -> User:
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        user = self.users[user_id]
        for key, value in user_data.items():
            setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        return user

    async def delete_user(self, user_id: str) -> None:
        if user_id not in self.users:
            raise HTTPException(status_code=404, detail="User not found")
        del self.users[user_id]

    async def update_user_roles(self, user_id: str, roles: List[str]) -> User:
        user = await self.get_user(user_id)
        user.roles = roles
        user.updated_at = datetime.now(timezone.utc)
        return user

    async def verify_user_email(self, user_id: str) -> User:
        user = await self.get_user(user_id)
        user.is_verified = True
        user.updated_at = datetime.now(timezone.utc)
        return user

    async def disable_user(self, user_id: str) -> User:
        user = await self.get_user(user_id)
        user.is_active = False
        user.updated_at = datetime.now(timezone.utc)
        return user

    async def enable_user(self, user_id: str) -> User:
        user = await self.get_user(user_id)
        user.is_active = True
        user.updated_at = datetime.now(timezone.utc)
        return user
    

    async def list_user_roles(self) -> List[UserRole]:
        user_roles = []
        for user in self.users.values():
            user_roles.append(UserRole(user_id=user.uid, roles=user.roles))
        return user_roles