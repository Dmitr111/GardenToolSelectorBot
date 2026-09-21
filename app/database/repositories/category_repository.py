from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.category import Category
from ..models.tool import Tool

class CategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Category]:
        result = await self.session.execute(select(Category))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Category:
        return await self.session.scalar(select(Category).where(Category.id == id))

    async def create(self, name: str, description: str = None) -> Category:
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.commit()
        return category

    async def update(self, id: int, name: str = None, description: str = None) -> bool:
        category = await self.get_by_id(id)
        if not category:
            return False
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
            
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        category = await self.get_by_id(id)
        if not category:
            return False
            
        await self.session.delete(category)
        await self.session.commit()
        return True

    async def get_tools_count(self, category_id: int) -> int:
        return await self.session.scalar(
            select(func.count(Tool.id)).where(Tool.category_id == category_id))