from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import *

class MaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Material]:
        result = await self.session.execute(select(Material))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Material:
        return await self.session.get(Material, id)
    
    async def get_by_ids(self, ids: list[int]) -> list[Material]:
        if not ids:
            return []
        result = await self.session.execute(
            select(Material).where(Material.id.in_(ids))
        )
        return result.scalars().all()
    
    async def get_by_tool_id(self, tool_id: int) -> list[Material]:
        result = await self.session.execute(
            select(Material)
            .join(ToolMaterial, ToolMaterial.material_id == Material.id)
            .where(ToolMaterial.tool_id == tool_id)
        )
        return result.scalars().all()

    async def create(self, name: str) -> Material:
        material = Material(name=name)
        self.session.add(material)
        await self.session.commit()
        return material

    async def update(self, id: int, name: str) -> bool:
        material = await self.get_by_id(id)
        if not material:
            return False
        
        material.name = name
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        material = await self.get_by_id(id)
        if not material:
            return False
            
        await self.session.delete(material)
        await self.session.commit()
        return True