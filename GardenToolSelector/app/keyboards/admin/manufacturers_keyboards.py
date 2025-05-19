from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

manage_manufacturers_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить производителя', callback_data='add_manufacturer')],
    [InlineKeyboardButton(text='✏️ Редактировать производителя', callback_data='edit_manufacturer')],
    [InlineKeyboardButton(text='🗑️ Удалить производителя', callback_data='delete_manufacturer')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')]
])

edit_manufacturer_options_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✏️ Изменить название', callback_data='edit_manufacturer_name')],
    [InlineKeyboardButton(text='🌍 Изменить страну', callback_data='edit_manufacturer_country')],
    [InlineKeyboardButton(text='🌐 Изменить веб-сайт', callback_data='edit_manufacturer_website')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_manufacturers')]
])

add_another_manufacturer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить еще одного производителя', callback_data='add_another_manufacturer')],
    [InlineKeyboardButton(text='🔙 К управлению производителями', callback_data='back_to_manufacturers')]
])

back_to_manufacturer_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 К управлению производителями', callback_data='back_to_manufacturers')]
])

async def manufacturers_edit_keyboard(manufacturers) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for manufacturer in manufacturers:
        keyboard.add(InlineKeyboardButton(
            text=manufacturer.name, 
            callback_data=f'editmanuf_{manufacturer.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_manufacturers'
    ))
    return keyboard.adjust(1).as_markup()

async def manufacturers_delete_keyboard(manufacturers) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for manufacturer in manufacturers:
        keyboard.add(InlineKeyboardButton(
            text=manufacturer.name, 
            callback_data=f'deletemanuf_{manufacturer.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_manufacturers'
    ))
    return keyboard.adjust(1).as_markup()