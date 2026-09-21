from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.proficiency_level import ProficiencyLevel
from ..models.user import User

class ProficiencyLevelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[ProficiencyLevel]:
        result = await self.session.execute(
            select(ProficiencyLevel).order_by(ProficiencyLevel.id))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> ProficiencyLevel:
        return await self.session.get(ProficiencyLevel, id)

    async def create(self, name: str, description: str = None) -> ProficiencyLevel:
        level = ProficiencyLevel(name=name, description=description)
        self.session.add(level)
        await self.session.commit()
        return level

    async def update(self, id: int, name: str = None, description: str = None) -> bool:
        level = await self.get_by_id(id)
        if not level:
            return False
            
        if name is not None:
            level.name = name
        if description is not None:
            level.description = description
            
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        level = await self.get_by_id(id)
        if not level:
            return False
            
        await self.session.delete(level)
        await self.session.commit()
        return True

    async def get_users_count(self, level_id: int) -> int:
        return await self.session.scalar(
            select(func.count(User.id))
            .where(User.proficiency_level_id == level_id)
        )