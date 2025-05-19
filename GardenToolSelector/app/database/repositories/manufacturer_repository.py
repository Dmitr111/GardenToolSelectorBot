from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.manufacturer import Manufacturer
from ..models.tool import Tool

class ManufacturerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[Manufacturer]:
        result = await self.session.execute(select(Manufacturer))
        return result.scalars().all()

    async def get_by_id(self, id: int) -> Manufacturer:
        return await self.session.scalar(select(Manufacturer).where(Manufacturer.id == id))

    async def create(self, name: str, country: str = None, website: str = None) -> Manufacturer:
        manufacturer = Manufacturer(name=name, country=country,  website=website)
        self.session.add(manufacturer)
        await self.session.commit()
        return manufacturer

    async def update(self, id: int, name: str = None, country: str = None, website: str = None) -> bool:
        manufacturer = await self.get_by_id(id)
        if not manufacturer:
            return False
            
        if name is not None:
            manufacturer.name = name
        if country is not None:
            manufacturer.country = country
        if website is not None:
            manufacturer.website = website
            
        await self.session.commit()
        return True

    async def delete(self, id: int) -> bool:
        manufacturer = await self.get_by_id(id)
        if not manufacturer:
            return False
            
        await self.session.delete(manufacturer)
        await self.session.commit()
        return True

    async def get_tools_count(self, manufacturer_id: int) -> int:
        return await self.session.scalar(
            select(func.count(Tool.id)).where(Tool.manufacturer_id == manufacturer_id))