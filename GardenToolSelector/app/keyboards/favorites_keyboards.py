from ..database.repositories import ToolRepository
from .selection_keyboards import build_tools_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

async def favorite_tools(favorites, session_instance: AsyncSession):
    tr = ToolRepository(session_instance)
    tools_list = await tr.get_by_ids(favorites)
    return await build_tools_keyboard(tools_list)