from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.user import User
from ..models.favorite import Favorite
from ..models.review import Review
from ..models.tool import Tool

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int):
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar()

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self.session.scalar(select(User).where(User.telegram_id == telegram_id))

    async def create(self, username: str, telegram_id: int, proficiency_level_id: int = None) -> User | None:
        user = await self.get_by_telegram_id(telegram_id)

        if not user:
            if proficiency_level_id is None:
                proficiency_level_id = 1
            user = User(username=username, telegram_id=telegram_id, proficiency_level_id=proficiency_level_id)
            self.session.add(user)
            await self.session.commit()
            return user
        return None

    async def update(self, telegram_id: int, **kwargs) -> bool:
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            return False

        for key, value in kwargs.items():
            setattr(user, key, value)

        await self.session.commit()
        return True

    async def make_admin(self, user_id: int) -> bool:
        user = await self.session.get(User, user_id)
        if user:
            user.is_admin = True
            await self.session.commit()
            return True
        return False

    async def is_admin(self, telegram_id: int) -> bool:
        user = await self.get_by_telegram_id(telegram_id)
        return bool(user and user.is_admin)

    async def get_favorites(self, user_id: int) -> list[int]:
        result = await self.session.scalars(select(Favorite.tool_id).where(Favorite.user_id == user_id))
        return result.all()

    async def get_reviews(self, user_id: int) -> list[int]:
        result = await self.session.scalars(select(Review.tool_id).where(Review.user_id == user_id))
        return result.all()

    async def get_admin_stats(self) -> dict[str, int]:
        total_users = await self.session.scalar(select(func.count(User.id)))

        total_admins = await self.session.scalar(
            select(func.count(User.id)).where(User.is_admin.is_(True))
        )

        total_tools = await self.session.scalar(select(func.count(Tool.id)))

        total_reviews = await self.session.scalar(select(func.count(Review.id)))

        new_users_today = await self.session.scalar(
            select(func.count(User.id)).where(
                func.date(User.registration_date) == func.current_date()
            )
        )

        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_tools": total_tools,
            "total_reviews": total_reviews,
            "new_users_today": new_users_today
        }
