from aiogram import F, Router
from aiogram.types import CallbackQuery
from ...database.db import async_session as session
from ...database.repositories import ProficiencyLevelRepository
from ...keyboards.admin.proficiency_levels_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_proficiency_levels')
async def manage_proficiency_levels(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление уровнями владения:",
        reply_markup=manage_proficiency_levels_kb()
    )
    await callback.answer()

@router.callback_query(F.data == 'view_levels')
async def view_proficiency_levels(callback: CallbackQuery):
    async with session() as session_instance:
        plr = ProficiencyLevelRepository(session_instance)
        levels = await plr.get_all()
        
        if not levels:
            await callback.answer("Нет доступных уровней владения")
            return
        
        levels_text = "Список уровней владения:\n\n"
        for level in levels:
            users_count = await plr.get_users_count(level.id)
            levels_text += (
                f"▪️ {level.name}\n"
                f"Описание: {level.description or 'нет описания'}\n"
                f"Пользователей: {users_count}\n\n"
            )
        
        await callback.message.edit_text(
            levels_text,
            reply_markup=back_to_manage_proficiency_levels_kb()
        )
    await callback.answer()
