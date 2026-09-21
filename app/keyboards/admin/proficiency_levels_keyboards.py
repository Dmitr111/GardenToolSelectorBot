from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def manage_proficiency_levels_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋 Просмотр уровней', callback_data='view_levels')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')],
    ])

def back_to_manage_proficiency_levels_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Назад', callback_data='manage_proficiency_levels')],
    ])

async def proficiency_levels_select_keyboard(levels) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for level in levels:
        keyboard.add(InlineKeyboardButton(
            text=level.name,
            callback_data=f'selectlevel_{level.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад',
        callback_data='back_to_recommendations'
    ))
    return keyboard.adjust(1).as_markup()