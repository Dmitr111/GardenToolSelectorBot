from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.recommendation import Recommendation

class RecommendationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Recommendation]:
        result = await self.session.execute(select(Recommendation))
        return result.scalars().all()

    async def get_all_with_details(self) -> list[Recommendation]:
        result = await self.session.execute(
            select(Recommendation)
            .options(
                joinedload(Recommendation.proficiency_level),
                joinedload(Recommendation.category)
            )
        )
        return result.scalars().all()

    async def get_with_details(self, id: int) -> Recommendation:
        result = await self.session.execute(
            select(Recommendation)
            .where(Recommendation.id == id)
            .options(
                joinedload(Recommendation.proficiency_level),
                joinedload(Recommendation.category)
            )
        )
        return result.scalar_one()

    async def get_by_id(self, id: int) -> Recommendation:
        return await self.session.get(Recommendation, id)
    
    async def get_by_category_id(self, category_id: int) -> Recommendation:
        return await self.session.scalar(select(Recommendation).where(Recommendation.category_id == category_id))


    async def create(self, proficiency_level_id: int, category_id: int, text: str) -> Recommendation:
        recommendation = Recommendation(
            proficiency_level_id=proficiency_level_id,
            category_id=category_id,
            text=text
        )
        self.session.add(recommendation)
        await self.session.commit()
        return recommendation

    async def update(self, id: int, **kwargs) -> bool:
        recommendation = await self.get_by_id(id)
        if not recommendation:
            return False
        
        for key, value in kwargs.items():
            setattr(recommendation, key, value)
            
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        recommendation = await self.get_by_id(id)
        if not recommendation:
            return False
            
        await self.session.delete(recommendation)
        await self.session.commit()
        return True