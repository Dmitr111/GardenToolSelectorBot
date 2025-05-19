from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

manage_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить категорию', callback_data='add_category')],
    [InlineKeyboardButton(text='✏️ Редактировать категорию', callback_data='edit_category')],
    [InlineKeyboardButton(text='🗑️ Удалить категорию', callback_data='delete_category')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')]
])

edit_category_options_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✏️ Изменить название', callback_data='edit_category_name')],
    [InlineKeyboardButton(text='📝 Изменить описание', callback_data='edit_category_description')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_categories')]
])

add_another_category_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить еще одну категорию', callback_data='add_another_category')],
    [InlineKeyboardButton(text='🔙 К управлению категориями', callback_data='back_to_categories')]
])

back_to_categories_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 К управлению категориями', callback_data='back_to_categories')]
])

async def categories_edit_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name, 
            callback_data=f'editcat_{category.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_categories'
    ))
    return keyboard.adjust(1).as_markup()

async def categories_delete_keyboard(categories) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name, 
            callback_data=f'deletecat_{category.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_categories'
    ))
    return keyboard.adjust(1).as_markup()