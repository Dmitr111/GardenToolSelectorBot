from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import *

class ToolMaterialRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_material_ids_by_tool(self, tool_id: int) -> list[int]:
        result = await self.session.execute(
            select(ToolMaterial.material_id)
            .where(ToolMaterial.tool_id == tool_id)
        )
        return [row[0] for row in result.fetchall()]

    async def delete_by_tool(self, tool_id: int) -> None:
        await self.session.execute(
            ToolMaterial.__table__.delete().where(ToolMaterial.tool_id == tool_id)
        )
        await self.session.commit()

    async def create(self, tool_id: int, material_id: int) -> None:
        tool_material = ToolMaterial(tool_id=tool_id, material_id=material_id)
        self.session.add(tool_material)
        await self.session.commit()

    async def get_count_by_material(self, material_id: int) -> int:
        return await self.session.scalar(
            select(func.count(ToolMaterial.id))
            .where(ToolMaterial.material_id == material_id)
        )