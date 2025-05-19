from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from ..database.db import async_session as session
from ..database.repositories import *
from .utils import tool_message as tm, review_messages as rm, show_tools_selection
from ..keyboards.selection_keyboards import *

router = Router()

@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        category_id = int(callback.data.split('_')[1])
        tools = await tr.get_by_category(category_id)
        if not tools:
            await callback.answer("В этой категории пока нет инструментов", show_alert=True)
            return

        await callback.answer("Вы выбрали категорию")
        try:
            await callback.message.edit_text(
                "Выберите инструмент из категории:",
                reply_markup=await select_tools(category_id, session_instance)
            )
        except TelegramBadRequest:
            await callback.answer("Сообщение устарело, попробуйте снова", show_alert=True)
            await show_tools_selection(callback.message)

@router.callback_query(F.data.startswith('tool_'))
async def tool_selected(callback: CallbackQuery):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        mr = ManufacturerRepository(session_instance)
        matr = MaterialRepository(session_instance)
        rr = RecommendationRepository(session_instance)
        tool_id = int(callback.data.split('_')[1])
        
        try:
            tool = await tr.get_by_id(tool_id)
            if not tool:
                await callback.answer("Инструмент не найден", show_alert=True)
                return

            manufacturer = await mr.get_by_id(tool.manufacturer_id)

            materials = await matr.get_by_tool_id(tool_id)
            material_names = ', '.join([m.name for m in materials])

            recommendations = await rr.get_by_category_id(tool.category_id)

            tool_name = f"{tool.name} ({tool.model})" if tool.model else tool.name
            message_text = (
                f"🏷️ Название: {tool_name}\n"
                f"📄 Описание: {tool.description or 'отсутствует'}\n"
                f"⭐ Средняя оценка: {tool.avg_rating or 'отсутствует'}\n"
                f"🏭 Производитель: {manufacturer.name if manufacturer else 'неизвестно'}\n"
                f"🌍 Страна: {manufacturer.country if manufacturer and manufacturer.country else 'неизвестно'}\n"
                f"🔗 Web-сайт: {manufacturer.website if manufacturer and manufacturer.website else 'отсутствует'}\n"
                f"🪙 Материал: {material_names or 'неизвестно'}\n"
                f"⚖️ Вес (в кг): {tool.weight or 'неизвестно'}\n"
                f"💰 Цена (в ₽): {tool.price or 'неизвестно'}\n"
                f"💡 Рекомендация:\n{recommendations.text or 'Нет рекомендаций'}"
            )

            await tm.delete(callback.bot)

            try:
                sent_message = await callback.message.edit_text(
                    message_text,
                    reply_markup=await get_tool_keyboard(callback.from_user.id, tool_id, session_instance)
                )
                tm.update(sent_message, tool_id)
                await callback.answer("Вы выбрали инструмент")
            except TelegramBadRequest:
                sent_message = await callback.message.answer(
                    message_text,
                    reply_markup=await get_tool_keyboard(callback.from_user.id, tool_id, session_instance)
                )
                tm.update(sent_message, tool_id)
                await callback.answer("Вы выбрали инструмент")
        except Exception as e:
            print(f"Ошибка при выводе инструмента: {e}")
            await callback.answer("Произошла ошибка, попробуйте снова", show_alert=True)


@router.callback_query(F.data == 'back_to_tool')
async def back_to_tool(callback: CallbackQuery):
    await rm.delete_all(callback.bot)
    await callback.answer()