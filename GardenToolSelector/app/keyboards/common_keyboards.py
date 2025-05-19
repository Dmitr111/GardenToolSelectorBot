from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from ..database.repositories import *
from sqlalchemy.ext.asyncio import AsyncSession

start_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='⚙️Профиль'), KeyboardButton(text='❓Помощь')],
    [KeyboardButton(text='🔨Выбор инструментов')],
    [KeyboardButton(text='✏️Применить Фильтры')],
    [KeyboardButton(text='🔍Поиск инструмента')]
], resize_keyboard=True, input_field_placeholder='Выбирите пункт меню.')

admin_panel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='📊 Статистика', callback_data='admin_stats')],
    [InlineKeyboardButton(text='👑 Назначить админа', callback_data='make_admin')],
    [InlineKeyboardButton(text='🗂️ Управление категориями', callback_data='manage_categories')],
    [InlineKeyboardButton(text='🏭 Управление производителями', callback_data='manage_manufacturers')],
    [InlineKeyboardButton(text='🛠️ Управление инструментами', callback_data='manage_tools')],
    [InlineKeyboardButton(text='🔩 Управление материалами', callback_data='manage_materials')],
    [InlineKeyboardButton(text='📝 Управление рекомендациями', callback_data='manage_recommendations')],
    [InlineKeyboardButton(text='📋 Уровни владения', callback_data='manage_proficiency_levels')],
    [InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile')]
])

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✖️ Отмена', callback_data='cancel')],
])

skip_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Пропустить', callback_data='skip')],
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
])

confirm_delete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Да, удалить', callback_data='confirm_delete')],
    [InlineKeyboardButton(text='❌ Нет, отменить', callback_data='cancel_delete')]
])

async def profile_keyboard(telegram_id: int, session_instance: AsyncSession) -> InlineKeyboardMarkup:
    ur = UserRepository(session_instance)
    user = await ur.get_by_telegram_id(telegram_id)

    buttons = [
        [
            InlineKeyboardButton(text='🌟 Избранное', callback_data='favorites'),
            InlineKeyboardButton(text='📝 Отзывы', callback_data='reviews')
        ],
        [
            InlineKeyboardButton(text='🔧 Изменить уровень владения', callback_data='update_proficiency')
        ]
    ]

    tr = ToolRepository(session_instance)
    tools_count = await tr.get_tools_count()
    if tools_count >= 2:
        buttons.append([InlineKeyboardButton(text='🔄 Сравнение инструментов', callback_data='compare_tools')])

    if user.is_admin:
        buttons.append([InlineKeyboardButton(text='⚙️ Админ-панель', callback_data='admin_panel')])

    return InlineKeyboardMarkup(inline_keyboard=buttons)