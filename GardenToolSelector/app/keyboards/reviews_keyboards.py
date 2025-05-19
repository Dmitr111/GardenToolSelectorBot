from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .selection_keyboards import build_tools_keyboard
from ..database.repositories import ToolRepository
from sqlalchemy.ext.asyncio import AsyncSession

review_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='✏️ Изменить', callback_data='update_review'),
        InlineKeyboardButton(text='🗑️ Удалить', callback_data='remove_from_review')
    ],
    [
        InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_tool')
    ]
])

review_rating_keyboards = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='1', callback_data='rate_1'),
    InlineKeyboardButton(text='2', callback_data='rate_2'),
    InlineKeyboardButton(text='3', callback_data='rate_3'),
    InlineKeyboardButton(text='4', callback_data='rate_4'),
    InlineKeyboardButton(text='5', callback_data='rate_5')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
], resize_keyboard=True, input_field_placeholder='Выбирите оценку для интсрумента.')

async def review_tools(review, session_instance: AsyncSession):
    tr = ToolRepository(session_instance)
    tools_list = await tr.get_by_ids(review)
    return await build_tools_keyboard(tools_list)

async def load_more_reviews_keyboard(offset: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Загрузить еще", callback_data=f"load_more_reviews_{offset}")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)