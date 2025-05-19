from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ...database.repositories import UserRepository

manage_tools_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='➕ Добавить инструмент', callback_data='add_tool')],
    [InlineKeyboardButton(text='✏️ Редактировать инструмент', callback_data='edit_tool')],
    [InlineKeyboardButton(text='🗑️ Удалить инструмент', callback_data='delete_tool')],
    [InlineKeyboardButton(text='💬 Просмотр отзывов', callback_data='view_tool_reviews')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='admin_panel')]
])

async def build_tools_keyboard(tools):
    keyboard = InlineKeyboardBuilder()
    for tool in tools:
        keyboard.add(InlineKeyboardButton(text=tool.name, callback_data=f'select_tool_{tool.id}'))
    return keyboard.as_markup()

async def build_reviews_keyboard(reviews, session_instance):
    keyboard = InlineKeyboardBuilder()
    ur = UserRepository(session_instance)
    for review in reviews:
        user = await ur.get_by_id(user_id=review.user_id)
        user_name = f'{user.username} ({str(user.telegram_id)})'
        keyboard.add(InlineKeyboardButton(text=user_name, callback_data=f'select_review_{review.id}'))
    return keyboard.as_markup()

async def build_review_actions_keyboard(review_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🗑️ Удалить отзыв', callback_data=f'delete_review_{review_id}')],
        [InlineKeyboardButton(text='🔙 Назад', callback_data='view_tool_reviews')]
    ])