from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ...database.db import async_session as session
from ...database.repositories import UserRepository
from ..states import AdminUser
from ...keyboards.common_keyboards import *

router = Router()

@router.callback_query(F.data == 'admin_panel')
async def load_more_reviews(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Это панель для администраторов:', reply_markup=admin_panel)
    await callback.answer()

@router.callback_query(F.data == "make_admin")
async def make_admin_handler(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminUser.waiting_for_user_telegram_id)
    await callback.message.edit_text(
        "Введите telegram_id пользователя, которого хотите сделать администратором:",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@router.message(AdminUser.waiting_for_user_telegram_id)
async def process_admin_username(message: Message, state: FSMContext, bot: Bot):
    async with session() as session_instance:
        telegram_id = int(message.text.strip())
        
        if not telegram_id:
            await message.answer("telegram_id не может быть пустым. Попробуйте еще раз.")
            return
        
        
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(telegram_id)
        
        if not user:
            await message.answer(f"Пользователь с таким telegram_id не найден в базе.")
            await state.clear()
            return
        
        await ur.make_admin(user.id)

        try:
            await bot.send_message(
                user.telegram_id,
                "🎉 Вам были предоставлены права администратора в боте GardenToolSelector!"
            )
        except Exception:
            pass
            
        await message.answer(f"✅ Пользователь @{user.username} успешно назначен администратором!")
        
        await state.clear()

@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: CallbackQuery):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        stats = await ur.get_admin_stats()
    
        await callback.message.answer("📊 Статистика бота:\n"
            f"👥 Пользователей: {stats['total_users']}\n"
            f"🛠️ Инструментов: {stats['total_tools']}\n"
            f"⭐ Отзывов: {stats['total_reviews']}\n"
            f"👑 Администраторов: {stats['total_admins']}\n"
            f"📅 Новых пользователей за день: {stats['new_users_today']}")

        await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_admin_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено.")
    await callback.answer()

@router.callback_query(F.data == 'back_to_profile')
async def admin_stats_handler(callback: CallbackQuery):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        await callback.message.edit_text(f'Это ваш профиль, {user.username}', 
                                        reply_markup = await profile_keyboard(callback.from_user.id, session_instance))