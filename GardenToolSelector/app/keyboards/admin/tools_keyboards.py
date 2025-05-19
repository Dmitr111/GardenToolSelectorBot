from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...database.models import *

manage_tools_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить инструмент', callback_data='add_tool')],
    [InlineKeyboardButton(text='✏️ Редактировать инструмент', callback_data='edit_tool')],
    [InlineKeyboardButton(text='🗑️ Удалить инструмент', callback_data='delete_tool')],
    [InlineKeyboardButton(text='💬 Просмотр отзывов', callback_data='view_tool_reviews')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')]
])

edit_tool_options_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✏️ Изменить название', callback_data='edit_tool_name')],
    [InlineKeyboardButton(text='📝 Изменить модель', callback_data='edit_tool_model')],
    [InlineKeyboardButton(text='📝 Изменить описание', callback_data='edit_tool_description')],
    [InlineKeyboardButton(text='🗂 Изменить категорию', callback_data='edit_tool_category')],
    [InlineKeyboardButton(text='🏭 Изменить производителя', callback_data='edit_tool_manufacturer')],
    [InlineKeyboardButton(text='🔩 Изменить материалы', callback_data='edit_tool_materials')],
    [InlineKeyboardButton(text='⚖️ Изменить вес', callback_data='edit_tool_weight')],
    [InlineKeyboardButton(text='💰 Изменить цену', callback_data='edit_tool_price')],
    [InlineKeyboardButton(text='🖼 Изменить изображения', callback_data='edit_tool_images')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_tools')]
])

add_another_tool_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить еще один инструмент', callback_data='add_another_tool')],
    [InlineKeyboardButton(text='🔙 К управлению инструментами', callback_data='back_to_tools')]
])

back_to_tools_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 К управлению инструментами', callback_data='back_to_tools')]
])

async def tools_edit_keyboard(tools: list[Tool]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for tool in tools:
        button_text = tool.name
        if tool.model:
            button_text += f" ({tool.model})"
            
        keyboard.add(InlineKeyboardButton(
            text=button_text, 
            callback_data=f'edittool_{tool.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_tools'
    ))
    return keyboard.adjust(1).as_markup()

async def tools_delete_keyboard(tools: list[Tool]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for tool in tools:
        keyboard.add(InlineKeyboardButton(
            text=tool.name, 
            callback_data=f'deletetool_{tool.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_tools'
    ))
    return keyboard.adjust(1).as_markup()

async def categories_select_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category.name, 
            callback_data=f'selectcat_{category.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_tools'
    ))
    return keyboard.adjust(1).as_markup()

async def manufacturers_select_keyboard(manufacturers: list[Manufacturer]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for manufacturer in manufacturers:
        keyboard.add(InlineKeyboardButton(
            text=manufacturer.name, 
            callback_data=f'selectmanuf_{manufacturer.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_tools'
    ))
    return keyboard.adjust(1).as_markup()

async def materials_select_keyboard(
    materials: list[Material], 
    selected_ids: list[int] = None,
    multi_select: bool = False
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    if selected_ids is None:
        selected_ids = []
    
    for material in materials:
        emoji = "✅ " if material.id in selected_ids else ""
        keyboard.add(InlineKeyboardButton(
            text=f"{emoji}{material.name}",
            callback_data=f"selectmaterial_{material.id}"
        ))
    
    if multi_select:
        confirm_button = InlineKeyboardButton(
            text="✔️ Подтвердить выбор",
            callback_data="confirm_materials"
        )
        confirm_button = confirm_button if selected_ids else InlineKeyboardButton(
            text="❌ Выберите хотя бы 1 материал",
            callback_data="no_materials_selected"
        )
        keyboard.add(confirm_button)

    keyboard.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back_to_tools"
    ))
    
    return keyboard.adjust(1).as_markup()