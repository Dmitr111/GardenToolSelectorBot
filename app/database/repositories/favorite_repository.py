from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.favorite import Favorite

class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_tool(self, user_id: int, tool_id: int) -> Favorite:
        result = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.tool_id == tool_id
            ))
        return result.scalar()

    async def get_user_favorites(self, user_id: int) -> list[int]:
        result = await self.session.execute(
            select(Favorite.tool_id).where(Favorite.user_id == user_id))
        return result.scalars().all()

    async def create(self, user_id: int, tool_id: int) -> Favorite:
        favorite = Favorite(user_id=user_id, tool_id=tool_id)
        self.session.add(favorite)
        await self.session.commit()
        return favorite

    async def delete(self, user_id: int, tool_id: int) -> bool:
        favorite = await self.get_by_user_and_tool(user_id, tool_id)
        if not favorite:
            return False
            
        await self.session.delete(favorite)
        await self.session.commit()
        return True

    async def exists(self, user_id: int, tool_id: int) -> bool:
        favorite = await self.get_by_user_and_tool(user_id, tool_id)
        return favorite is not None