from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from ..database.db import async_session as session
from ..database.repositories import ToolRepository, ManufacturerRepository, MaterialRepository
from .states import CompareTools
from .utils import tool_message as tm
from ..keyboards.comparison_keyboards import *
from ..keyboards.selection_keyboards import *

router = Router()

@router.callback_query(F.data.startswith('compare_from_tool_'))
async def start_comparing_from_tool(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tool_id = int(callback.data.split('_')[-1])
        tool = await tr.get_by_id(tool_id)

        if not tool:
            await callback.answer("Инструмент не найден")
            return

        await state.update_data(first_tool_id=tool_id, first_tool_name=tool.name)
        await callback.message.edit_text(
            f"Выбран первый инструмент: {tool.name}\nВыберите второй инструмент:",
            reply_markup=await all_tools_for_comparing(session_instance, exclude_tool_id=tool_id)
        )
        await state.set_state(CompareTools.waiting_for_second_tool)
        await callback.answer()

@router.callback_query(F.data == 'compare_tools')
async def start_comparing_from_tool(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        await callback.message.edit_text(
            "Выберите первый инструмент:",
            reply_markup=await all_tools_for_comparing(session_instance)
        )
        await state.set_state(CompareTools.waiting_for_first_tool)
        await callback.answer()

@router.callback_query(F.data.startswith('compare_'), CompareTools.waiting_for_first_tool)
async def select_first_tool(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tool_id = int(callback.data.split('_')[1])
        tool = await tr.get_by_id(tool_id)

        if not tool:
            await callback.answer("Инструмент не найден")
            return

        await state.update_data(first_tool_id=tool_id, first_tool_name=tool.name)
        await callback.message.edit_text(
            f"Выбран первый инструмент: {tool.name}\nВыберите второй инструмент:",
            reply_markup=await all_tools_for_comparing(session_instance, exclude_tool_id=tool_id)
        )
        await state.set_state(CompareTools.waiting_for_second_tool)
        await callback.answer()

@router.callback_query(F.data.startswith('compare_'), CompareTools.waiting_for_second_tool)
async def select_second_tool(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        mr = ManufacturerRepository(session_instance)
        mat_repo = MaterialRepository(session_instance)
        tool_id = int(callback.data.split('_')[1])
        data = await state.get_data()
        first_tool_id = data['first_tool_id']

        first_tool = await tr.get_by_id(first_tool_id)
        second_tool = await tr.get_by_id(tool_id)

        if not first_tool or not second_tool:
            await callback.answer("Один из инструментов не найден")
            await state.clear()
            return

        first_manufacturer = await mr.get_by_id(first_tool.manufacturer_id)
        second_manufacturer = await mr.get_by_id(second_tool.manufacturer_id)

        first_materials = await mat_repo.get_by_tool_id(first_tool_id)
        second_materials = await mat_repo.get_by_tool_id(tool_id)

        first_materials_text = ', '.join([m.name for m in first_materials]) if first_materials else 'неизвестно'
        second_materials_text = ', '.join([m.name for m in second_materials]) if second_materials else 'неизвестно'

        comparison_text = (
            f"🔍 Сравнение инструментов:\n\n"
            f"1️⃣ {first_tool.name} ({first_tool.model or 'неизвестно'})\n"
            f"2️⃣ {second_tool.name} ({second_tool.model or 'неизвестно'})\n\n"
            f"🏭 Производитель:\n1: {first_manufacturer.name if first_manufacturer else 'неизвестно'}\n"
            f"2: {second_manufacturer.name if second_manufacturer else 'неизвестно'}\n\n"
            f"🔩 Материалы:\n1: {first_materials_text}\n2: {second_materials_text}\n\n"
            f"⚖️ Вес (в кг):\n1: {first_tool.weight or 'неизвестно'}\n2: {second_tool.weight or 'неизвестно'}\n\n"
            f"💰 Цена (в ₽):\n1: {first_tool.price or 'неизвестно'}\n2: {second_tool.price or 'неизвестно'}\n"
        )

        await callback.message.edit_text(
            comparison_text,
            reply_markup=get_comparison_keyboard(first_tool_id, tool_id)
        )
        await state.clear()
        await callback.answer()