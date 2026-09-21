from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.tool import Tool
from ..models.review import Review
from ..models.favorite import Favorite


class ToolRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Tool]:
        result = await self.session.execute(select(Tool).order_by(Tool.name))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Tool:
        return await self.session.scalar(select(Tool).where(Tool.id == id))

    async def get_all_except(self, tool_id: int) -> list[Tool]:
        result = await self.session.execute(
            select(Tool).where(Tool.id != tool_id).order_by(Tool.name)
        )
        return result.scalars().all()

    async def get_by_category(self, category_id: int) -> list[Tool]:
        return await self.session.scalars(
            select(Tool).where(Tool.category_id == category_id))
    
    async def get_by_ids(self, tool_ids:str) -> list[Tool]:
        return await self.session.scalars(select(Tool).where(Tool.id.in_(tool_ids)))
    
    async def get_filtered_tools(self, filters: dict) -> list[Tool]:
        query = select(Tool)
        
        if "category_id" in filters:
            query = query.where(Tool.category_id == filters["category_id"])
        if "manufacturer_id" in filters:
            query = query.where(Tool.manufacturer_id == filters["manufacturer_id"])
        if "min_price" in filters:
            query = query.where(Tool.price >= filters["min_price"])
        if "max_price" in filters:
            query = query.where(Tool.price <= filters["max_price"])
        if "min_rating" in filters or "max_rating" in filters:
            query = query.join(Review, Review.tool_id == Tool.id, isouter=True)
            query = query.group_by(Tool.id)
            if "min_rating" in filters:
                query = query.having(func.coalesce(func.avg(Review.rating), 0) >= filters["min_rating"])
            if "max_rating" in filters:
                query = query.having(func.coalesce(func.avg(Review.rating), 0) <= filters["max_rating"])
        
        result = await self.session.execute(query.order_by(Tool.name))
        return result.scalars().all()

    async def search(self, query: str, limit: int = 20) -> list[Tool]:
        result = await self.session.execute(
            select(Tool).where(
                (func.concat(Tool.name, ' ', Tool.model).ilike(f"%{query}%"))
                    ).limit(limit)
            )
        return result.scalars().all()

    async def create(self, name: str, category_id: int, manufacturer_id: int, **kwargs) -> Tool:
        tool = Tool(
            name=name,
            category_id=category_id,
            manufacturer_id=manufacturer_id,
            **kwargs
        )
        self.session.add(tool)
        await self.session.commit()
        return tool

    async def update(self, id: int, **kwargs) -> bool:
        tool = await self.get_by_id(id)
        if not tool:
            return False
            
        for key, value in kwargs.items():
            setattr(tool, key, value)
            
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        tool = await self.get_by_id(id)
        if not tool:
            return False
            
        await self.session.delete(tool)
        await self.session.commit()
        return True

    async def get_reviews_count(self, tool_id: int) -> int:
        return await self.session.scalar(
            select(func.count(Review.id)).where(Review.tool_id == tool_id))

    async def get_favorites_count(self, tool_id: int) -> int:
        return await self.session.scalar(
            select(func.count(Favorite.id)).where(Favorite.tool_id == tool_id))
    
    async def get_tools_count(self) -> int:
        return await self.session.scalar(select(func.count(Tool.id)))