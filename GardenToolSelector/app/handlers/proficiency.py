from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..database.db import async_session as session
from ..database.repositories import UserRepository
from .states import UpdateProficiency
from ..keyboards.proficiency_keyboards import *

router = Router()

@router.callback_query(F.data.startswith('select_proficiency_'), UpdateProficiency.waiting_for_level)
async def select_proficiency(callback: CallbackQuery, state: FSMContext):
    proficiency_id = int(callback.data.split('_')[-1])
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        success = await ur.update(callback.from_user.id, proficiency_level_id=proficiency_id)

        if success:
            await callback.message.edit_text("Уровень владения успешно обновлен!")
        else:
            await callback.message.edit_text("Ошибка обновления уровня владения.")

        await state.clear()

@router.callback_query(F.data == 'update_proficiency')
async def change_proficiency(message: Message, state: FSMContext):
    async with session() as session_instance:
        await message.answer("Выберите ваш новый уровень владения:", 
                            reply_markup=await get_proficiency_keyboard(session_instance))
        await state.set_state(UpdateProficiency.waiting_for_level)