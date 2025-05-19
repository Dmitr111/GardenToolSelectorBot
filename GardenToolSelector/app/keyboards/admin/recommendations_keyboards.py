from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

manage_recommendations_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить рекомендацию', callback_data='add_recommendation')],
    [InlineKeyboardButton(text='✏️ Редактировать рекомендацию', callback_data='edit_recommendation')],
    [InlineKeyboardButton(text='🗑️ Удалить рекомендацию', callback_data='delete_recommendation')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')]
])

edit_recommendation_options_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✏️ Изменить уровень', callback_data='edit_recommendation_level')],
    [InlineKeyboardButton(text='📝 Изменить категорию', callback_data='edit_recommendation_category')],
    [InlineKeyboardButton(text='📝 Изменить текст', callback_data='edit_recommendation_text')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_recommendations')]
])

add_another_recommendation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить еще одну рекомендацию', callback_data='add_another_recommendation')],
    [InlineKeyboardButton(text='🔙 К управлению рекомендациями', callback_data='back_to_recommendations')]
])

back_to_recommendations_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🔙 К управлению рекомендациями', callback_data='back_to_recommendations')]
])

async def recommendations_edit_keyboard(recommendations) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for recommendation in recommendations:
        keyboard.add(InlineKeyboardButton(
            text=f"{recommendation.proficiency_level.name} - {recommendation.category.name}", 
            callback_data=f'editrec_{recommendation.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_recommendations'
    ))
    return keyboard.adjust(1).as_markup()

async def recommendations_delete_keyboard(recommendations) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for recommendation in recommendations:
        keyboard.add(InlineKeyboardButton(
            text=f"{recommendation.proficiency_level.name} - {recommendation.category.name}", 
            callback_data=f'delrec_{recommendation.id}'
        ))
    keyboard.add(InlineKeyboardButton(
        text='🔙 Назад', 
        callback_data='back_to_recommendations'
    ))
    return keyboard.adjust(1).as_markup()

async def categories_select_keyboard(categories) -> InlineKeyboardMarkup:
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