from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..database.repositories import ToolRepository
from sqlalchemy.ext.asyncio import AsyncSession

async def all_tools_for_comparing(session_instance: AsyncSession, exclude_tool_id: int = None) -> InlineKeyboardMarkup:
    repository = ToolRepository(session_instance)
    tools = await repository.get_all()
    keyboard = InlineKeyboardBuilder()
    
    for tool in tools:
        if exclude_tool_id is not None and tool.id == exclude_tool_id:
            continue
        keyboard.add(InlineKeyboardButton(
            text=f'{tool.name} ({tool.model})',
            callback_data=f'compare_{tool.id}'
        ))
    
    keyboard.add(InlineKeyboardButton(
        text='Отмена',
        callback_data='cancel'
    ))
    
    return keyboard.adjust(1).as_markup()

def get_comparison_keyboard(first_tool_id: int, second_tool_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='↩️ К инструменту 1', callback_data=f'tool_{first_tool_id}'),
            InlineKeyboardButton(text='↪️ К инструменту 2', callback_data=f'tool_{second_tool_id}')
        ],
        [InlineKeyboardButton(text='🔙 В меню', callback_data='back_to_profile')]
    ])