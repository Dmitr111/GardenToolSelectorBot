from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from ..database.repositories import *
from sqlalchemy.ext.asyncio import AsyncSession

async def get_proficiency_keyboard(session_instance: AsyncSession) -> InlineKeyboardMarkup:
    proficiency_repository = ProficiencyLevelRepository(session_instance)
    levels = await proficiency_repository.get_all()
    buttons = [[InlineKeyboardButton(text=level.name, callback_data=f'select_proficiency_{level.id}')]
              for level in levels]
    return InlineKeyboardMarkup(inline_keyboard=buttons)