from aiogram import F, Router
from aiogram.types import CallbackQuery
from ..database.db import async_session as session
from ..database.repositories import UserRepository, FavoriteRepository
from .utils import tool_message as tm
from ..keyboards.selection_keyboards import *
from ..keyboards.reviews_keyboards import *
from ..keyboards.favorites_keyboards import *

router = Router()

@router.callback_query(F.data == 'add_to_favorites')
async def add_to_favorites(callback: CallbackQuery):
    async with session() as session_instance:
        if not tm.message_id:
            await callback.answer('Ошибка: сообщение с инструментом не найдено')
            return
        
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        fr = FavoriteRepository(session_instance)
        is_create = await fr.create(user.id, tm.tool_id)

        if is_create:
            await callback.answer('Инструмент добавлен в избранное.')
        else:
            await callback.answer('Произошла ошибка при добавлении.')

        try:
            await callback.bot.edit_message_reply_markup(
                chat_id=tm.chat_id,
                message_id=tm.message_id,
                reply_markup = await get_tool_keyboard(callback.from_user.id,  tm.tool_id, session_instance))
        except Exception:
            pass

@router.callback_query(F.data == 'remove_from_favorites')
async def remove_from_favorites(callback: CallbackQuery):
    async with session() as session_instance:
        if not tm.message_id:
            await callback.answer('Ошибка: сообщение с инструментом не найдено')
            return
        
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        fr = FavoriteRepository(session_instance)
        await fr.delete(user.id,  tm.tool_id)
        await callback.answer('Инструмент удален из избранного')

        try:
            await callback.bot.edit_message_reply_markup(
                chat_id=tm.chat_id,
                message_id=tm.message_id,
                reply_markup = await get_tool_keyboard(callback.from_user.id, tm.tool_id, session_instance))
        except Exception:
            pass

@router.callback_query(F.data == 'favorites')
async def favorites(callback: CallbackQuery):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        fr = FavoriteRepository(session_instance)
        favorites = await fr.get_user_favorites(user.id)

        if not favorites:
            await callback.answer('У вас пока нет избранных инструментов.', show_alert=True)
        else:
            await callback.message.edit_text('Избранные инструменты:', 
                                            reply_markup = await favorite_tools(favorites, session_instance))    