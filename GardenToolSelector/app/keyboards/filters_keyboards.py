from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ..database.repositories import CategoryRepository, ManufacturerRepository

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_filters_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📂 По категории", callback_data="filter_by_category"),
        InlineKeyboardButton(text="🏭 По производителю", callback_data="filter_by_manufacturer")
    )
    builder.row(
        InlineKeyboardButton(text="💰 По цене", callback_data="filter_by_price"),
        InlineKeyboardButton(text="⭐ По рейтингу", callback_data="filter_by_rating")
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Сбросить фильтры", callback_data="reset_filters"),
        InlineKeyboardButton(text="✅ Применить фильтры", callback_data="apply_filters")
    )
    return builder.as_markup()


async def select_categories_for_filter(session):
    cr = CategoryRepository(session)
    categories = await cr.get_all()
    
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.add(InlineKeyboardButton(
            text=category.name,
            callback_data=f"filter_category_{category.id}"
        ))
    builder.adjust(1)
    return builder.as_markup()

async def select_manufacturers_for_filter(session):
    mr = ManufacturerRepository(session)
    manufacturers = await mr.get_all()
    
    builder = InlineKeyboardBuilder()
    for manufacturer in manufacturers:
        builder.add(InlineKeyboardButton(
            text=manufacturer.name,
            callback_data=f"filter_manufacturer_{manufacturer.id}"
        ))
    builder.adjust(2)
    return builder.as_markup()

async def select_filtered_tools(session, tools):
    builder = InlineKeyboardBuilder()
    for tool in tools:
        builder.add(InlineKeyboardButton(
            text=tool.name,
            callback_data=f"tool_{tool.id}"
        ))
    builder.adjust(2)
    return builder.as_markup()