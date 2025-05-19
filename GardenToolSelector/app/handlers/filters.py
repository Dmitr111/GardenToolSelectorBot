from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from ..database.db import async_session as session
from ..database.repositories import ToolRepository, CategoryRepository, ManufacturerRepository
from ..keyboards.filters_keyboards import *
from .states import FilterTools
from .utils import current_filters

router = Router()

async def show_filter_options(message: Message, state: FSMContext):
    filter_text = "Текущие фильтры:\n"
    
    if "category_id" in current_filters:
        async with session() as session_instance:
            cr = CategoryRepository(session_instance)
            category = await cr.get_by_id(current_filters["category_id"])
            if category:
                filter_text += f"Категория: {category.name}\n"
                
    if "manufacturer_id" in current_filters:
        async with session() as session_instance:
            mr = ManufacturerRepository(session_instance)
            manufacturer = await mr.get_by_id(current_filters["manufacturer_id"])
            if manufacturer:
                filter_text += f"Производитель: {manufacturer.name}\n"
                
    if "min_price" in current_filters:
        filter_text += f"Минимальная цена: {current_filters['min_price']}\n"
    if "max_price" in current_filters:
        filter_text += f"Максимальная цена: {current_filters['max_price']}\n"
    if "min_rating" in current_filters:
        filter_text += f"Минимальный рейтинг: {current_filters['min_rating']}\n"
    if "max_rating" in current_filters:
        filter_text += f"Максимальный рейтинг: {current_filters['max_rating']}\n"
    
    if len(current_filters) == 0:
        filter_text = "Фильтры не установлены\n"
    
    await message.answer(
        f"{filter_text}\nВыберите параметры фильтрации:",
        reply_markup=get_filters_keyboard()
    )
    await state.set_state(FilterTools.applying_filters)


@router.callback_query(F.data == "reset_filters")
async def reset_filters(callback: CallbackQuery, state: FSMContext):
    current_filters.clear()
    await callback.answer("Фильтры сброшены")
    await callback.message.edit_text(
        "Фильтры сброшены. Выберите параметры фильтрации:",
        reply_markup=get_filters_keyboard()
    )

@router.callback_query(F.data == "filter_by_category")
async def filter_by_category(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        if not categories:
            await callback.answer("Категории не найдены", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Выберите категорию для фильтрации:",
            reply_markup=await select_categories_for_filter(session_instance)
        )
        await state.set_state(FilterTools.waiting_for_category)

@router.callback_query(F.data.startswith("filter_category_"), FilterTools.waiting_for_category)
async def category_selected_for_filter(callback: CallbackQuery, state: FSMContext):
    try:
        category_id = int(callback.data.split("_")[2])
        current_filters["category_id"] = category_id
        await callback.answer("Категория выбрана")
        await show_filter_options(callback.message, state)
    except (IndexError, ValueError):
        await callback.answer("Ошибка: неверный формат данных")

@router.callback_query(F.data == "filter_by_manufacturer")
async def filter_by_manufacturer(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        mr = ManufacturerRepository(session_instance)
        manufacturers = await mr.get_all()
        if not manufacturers:
            await callback.answer("Производители не найдены", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Выберите производителя для фильтрации:",
            reply_markup=await select_manufacturers_for_filter(session_instance)
        )
        await state.set_state(FilterTools.waiting_for_manufacturer)

@router.callback_query(F.data.startswith("filter_manufacturer_"), FilterTools.waiting_for_manufacturer)
async def manufacturer_selected_for_filter(callback: CallbackQuery, state: FSMContext):
    try:
        manufacturer_id = int(callback.data.split("_")[2])
        current_filters["manufacturer_id"] = manufacturer_id
        await callback.answer("Производитель выбран")
        await show_filter_options(callback.message, state)
    except (IndexError, ValueError):
        await callback.answer("Ошибка: неверный формат данных")

@router.callback_query(F.data == "filter_by_price")
async def filter_by_price(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите минимальную цену (только число):")
    await state.set_state(FilterTools.waiting_for_min_price)

@router.message(FilterTools.waiting_for_min_price)
async def min_price_entered(message: Message, state: FSMContext):
    try:
        min_price = float(message.text)
        current_filters["min_price"] = min_price
        await message.answer("Теперь введите максимальную цену (только число):")
        await state.set_state(FilterTools.waiting_for_max_price)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")

@router.message(FilterTools.waiting_for_max_price)
async def max_price_entered(message: Message, state: FSMContext):
    try:
        max_price = float(message.text)
        if max_price < current_filters.get("min_price", 0):
            await message.answer("Максимальная цена должна быть больше минимальной")
            return
        
        current_filters["max_price"] = max_price
        await show_filter_options(message, state)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")

@router.callback_query(F.data == "filter_by_rating")
async def filter_by_rating(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Введите минимальный рейтинг (от 1 до 5):")
    await state.set_state(FilterTools.waiting_for_min_rating)

@router.message(FilterTools.waiting_for_min_rating)
async def min_rating_entered(message: Message, state: FSMContext):
    try:
        min_rating = float(message.text)
        if not 1 <= min_rating <= 5:
            await message.answer("Рейтинг должен быть от 1 до 5")
            return
        
        current_filters["min_rating"] = min_rating
        await message.answer("Теперь введите максимальный рейтинг (от 1 до 5):")
        await state.set_state(FilterTools.waiting_for_max_rating)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")

@router.message(FilterTools.waiting_for_max_rating)
async def max_rating_entered(message: Message, state: FSMContext):
    try:
        max_rating = float(message.text)
        if not 1 <= max_rating <= 5 or max_rating < current_filters.get("min_rating", 1):
            await message.answer("Максимальный рейтинг должен быть от 1 до 5 и больше минимального")
            return
        
        current_filters["max_rating"] = max_rating
        await show_filter_options(message, state)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число")

@router.callback_query(F.data == "apply_filters")
async def apply_filters(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tools = await tr.get_filtered_tools(current_filters)
        
        if not tools:
            await callback.answer("Инструменты по заданным фильтрам не найдены", show_alert=True)
            return
        
        await callback.message.edit_text(
            "Результаты фильтрации:",
            reply_markup=await select_filtered_tools(session_instance, tools)
        )
        await state.clear()