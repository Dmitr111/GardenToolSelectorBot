from aiogram import F, Router
from aiogram.types import CallbackQuery
from ...database.db import async_session as session
from ...database.repositories import MaterialRepository
from ...keyboards.admin.materials_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_materials')
async def manage_materials(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление материалами инструментов:",
        reply_markup=manage_materials_kb()
    )
    await callback.answer()

@router.callback_query(F.data == 'view_materials')
async def view_materials(callback: CallbackQuery):
    async with session() as session_instance:
        mr = MaterialRepository(session_instance)
        materials = await mr.get_all()
        
        if not materials:
            await callback.answer("Нет доступных материалов", show_alert=True)
            return
        
        materials_text = "📂 Список материалов:\n\n"
        for material in materials:
            materials_text += f"▪️ {material.name}\n"
        
        await callback.message.edit_text(
            materials_text,
            reply_markup=back_to_manage_materials_kb()
        )
    await callback.answer()