from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..database.repositories import UserRepository, FavoriteRepository, ReviewRepository, ToolRepository, CategoryRepository
from sqlalchemy.ext.asyncio import AsyncSession

async def create_search_results_keyboard(tools: list) -> InlineKeyboardMarkup:
    buttons = []
    for tool in tools:
        buttons.append(
            [InlineKeyboardButton(text=tool.name, callback_data=f"tool_{tool.id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_tool_keyboard(telegram_id: int, tool_id: int, session_instance: AsyncSession) -> InlineKeyboardMarkup:
    ur = UserRepository(session_instance)
    user = await ur.get_by_telegram_id(telegram_id)
    fr = FavoriteRepository(session_instance)
    is_favorite = await fr.exists(user.id, tool_id)
    rr = ReviewRepository(session_instance)
    is_review = await rr.exists(user.id, tool_id)
    
    buttons = [
        [
            InlineKeyboardButton(
                text='💔 Из избранного' if is_favorite else '❤️ В избранное',
                callback_data='remove_from_favorites' if is_favorite else 'add_to_favorites'
            ),
            InlineKeyboardButton(
                text='✍️ Ваш отзыв' if is_review else '📝 Написать отзыв',
                callback_data='show_review' if is_review else 'write_review'
            )
        ],
        [InlineKeyboardButton(text='👥 Отзывы пользователей', callback_data='view_reviews')],
    ]
    
    tr = ToolRepository(session_instance)
    tools_count = await tr.get_tools_count()
    if tools_count >= 2:
        buttons.append([InlineKeyboardButton(text='🔄 Сравнить с другим', callback_data=f'compare_from_tool_{tool_id}')])
    
    buttons.append([InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_tools_in_category')])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def select_categories(session_instance: AsyncSession) -> InlineKeyboardMarkup:
    cr = CategoryRepository(session_instance)
    categories = await cr.get_all()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'category_{category.id}'))

    return keyboard.adjust(1).as_markup()

async def select_tools(category_id: int, session_instance: AsyncSession):
    tr = ToolRepository(session_instance)
    tools_list = await tr.get_by_category(category_id)
    keyboard = InlineKeyboardBuilder()
    if isinstance(tools_list, str):
        keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile'))
        return tools_list, keyboard.adjust(1).as_markup()
    
    for tool in tools_list:
        button_text = tool.name + f" ({tool.model})"
        
        keyboard.add(InlineKeyboardButton(
            text=button_text, 
            callback_data=f'tool_{tool.id}'
        ))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile'))
    return keyboard.adjust(1).as_markup()
    
async def build_tools_keyboard(tools_list):
    keyboard = InlineKeyboardBuilder()
    if isinstance(tools_list, str):
        keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile'))
        return tools_list, keyboard.adjust(1).as_markup()
    
    for tool in tools_list:
        button_text = tool.name
        if tool.model:
            button_text += f" ({tool.model})"
        
        keyboard.add(InlineKeyboardButton(
            text=button_text, 
            callback_data=f'tool_{tool.id}'
        ))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_profile'))
    return keyboard.adjust(1).as_markup()