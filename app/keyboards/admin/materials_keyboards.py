from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def manage_materials_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📋 Просмотр материалов', callback_data='view_materials')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')],
    ])

def back_to_manage_materials_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔙 Назад', callback_data='manage_materials')],
    ])
