from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton
from .states import Search
from ..database.db import async_session as session
from ..database.repositories import ToolRepository
from ..keyboards.selection_keyboards import *

router = Router()

@router.message(Search.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    async with session() as session_instance:
        search_query = message.text.strip()
        if len(search_query) < 2:
            await message.answer("Слишком короткий запрос. Введите минимум 2 символа.")
            return

        tr = ToolRepository(session_instance)
        found_tools = await tr.search(search_query)
        
        if not found_tools:
            await message.answer("Инструменты по вашему запросу не найдены.")
            await state.clear()
            return
        
        keyboard = await create_search_results_keyboard(found_tools[:10])
        
        if len(found_tools) > 10:
            await state.update_data(search_results=found_tools, offset=5)
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text='Показать еще', callback_data='show_more_results')]
            )
        
        await message.answer('Результаты поиска:', reply_markup=keyboard)
        await state.clear()

@router.callback_query(F.data == 'show_more_results')
async def show_more_results(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    found_tools = data.get('search_results', [])
    offset = data.get('offset', 0)
    
    if not found_tools or offset >= len(found_tools):
        await callback.answer('Больше результатов нет')
        return
    
    keyboard = await create_search_results_keyboard(found_tools[offset:offset+10])
    
    new_offset = offset + 10
    if new_offset < len(found_tools):
        await state.update_data(offset=new_offset)
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text='Показать еще', callback_data='show_more_results')]
        )
    
    await callback.message.edit_text('Дополнительные результаты:', reply_markup=keyboard)
    await callback.answer()