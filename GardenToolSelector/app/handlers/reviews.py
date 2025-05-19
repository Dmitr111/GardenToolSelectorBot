from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from ..database.db import async_session as session
from ..database.repositories import *
from .states import Reviews
from .utils import review_messages as rm, tool_message as tm
from ..keyboards.common_keyboards import *
from ..keyboards.reviews_keyboards import *
from ..keyboards.selection_keyboards import *

router = Router()

@router.callback_query(F.data == 'write_review')
async def write_review_first(callback: CallbackQuery, state: FSMContext):
    await rm.delete_all(callback.bot)
    await state.set_state(Reviews.waiting_for_text)
    sent_message = await callback.message.answer('Введите текст отзыва:', reply_markup=cancel_keyboard)
    rm.add(sent_message)
    await callback.answer()

@router.message(Reviews.waiting_for_text)
async def write_review_second(message: Message, state: FSMContext):
    review_text = message.text.strip()
    if len(review_text) < 10:
        await message.answer("Слишком короткий отзыв. Введите минимум 10 символов.")
        return

    await rm.delete_all(message.bot)
    await state.update_data(waiting_for_text=review_text)
    await state.set_state(Reviews.waiting_for_rating)

    await message.delete()
    sent_message = await message.answer('Выберите оценку:', reply_markup=review_rating_keyboards)
    rm.add(sent_message)

@router.callback_query(F.data.startswith('rate_'), Reviews.waiting_for_rating)
async def write_review_waiting_for_rating(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        try:
            rating = int(callback.data.split('_')[1])
            await state.update_data(waiting_for_rating=rating)
            await rm.delete_all(callback.bot)

            data = await state.get_data()
            ur = UserRepository(session_instance)
            user = await ur.get_by_telegram_id(callback.from_user.id)
            tool_id = tm.tool_id
            
            if not tool_id:
                await callback.answer('Ошибка: инструмент не найден')
                return
            
            rr = ReviewRepository(session_instance)
            is_review = await rr.exists(user.id, tool_id)
            
            if not is_review:
                await rr.create_or_update(user.id, tool_id, data['waiting_for_text'], rating)
                await callback.answer('Отзыв добавлен', show_alert=True)
            else:
                await rr.create_or_update(user.id, tool_id, data['waiting_for_text'], rating)
                await callback.answer('Отзыв обновлен', show_alert=True)

            if tm.message_id:
                try:
                    await callback.bot.edit_message_reply_markup(
                        chat_id=tm.chat_id,
                        message_id=tm.message_id,
                        reply_markup=await get_tool_keyboard(callback.from_user.id, tool_id, session_instance)
                    )
                except TelegramBadRequest:
                    tr = ToolRepository(session_instance)
                    tool_data = await tr.get_by_id(tool_id)
                    mr = ManufacturerRepository(session_instance)
                    manufacturer_data = await mr.get_by_id(tool_data.manufacturer_id)

                    message_text = (
                        f'Название: {tool_data.name}\n'
                        f'Описание: {tool_data.description or "отсутствует"}\n'
                        f'Средняя оценка: {tool_data.avg_rating or "нет"}\n'
                        f'Производитель: {manufacturer_data.name or "неизвестно"}\n'
                        f'Страна: {manufacturer_data.country or "неизвестно"}\n'
                        f'Web-сайт: {manufacturer_data.website or "неизвестно"}\n'
                        f'Вес (кг): {tool_data.weight or "неизвестно"}\n'
                        f'Цена (₽): {tool_data.price or "неизвестно"}'
                    )
                    sent_message = await callback.message.answer(
                        message_text,
                        reply_markup=await get_tool_keyboard(callback.from_user.id, tool_id, session_instance)
                    )
                    tm.update(sent_message, tool_id)
            
            await state.clear()
        except Exception as e:
            await callback.answer('Произошла ошибка, попробуйте снова')

@router.callback_query(F.data == 'show_review')
async def show_review(callback: CallbackQuery):
    async with session() as session_instance:
        await rm.delete_all(callback.bot)
        
        if not tm.tool_id:
            await callback.answer("Не удалось определить инструмент")
            return
        
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        rr = ReviewRepository(session_instance)
        review = await rr.get_by_user_and_tool(user.id, tm.tool_id)
        
        if not review:
            await callback.answer("Вы еще не оставляли отзыв на этот инструмент", show_alert=True)
            return
        
        review_text = (
            f'Ваш отзыв:\n{review.text}\n'
            f'Ваша оценка: {review.rating}\n'
            f'Дата добавления: {review.review_date.strftime("%Y-%m-%d %H:%M:%S")}'
        )
        
        sent_message = await callback.message.answer(
            review_text,
            reply_markup=review_keyboard
        )
        
        rm.add(sent_message)
        await callback.answer()            

@router.callback_query(F.data == 'reviews')
async def reviews(callback: CallbackQuery):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)
        reviews = await ur.get_reviews(user.id)
        
        if not reviews:
            await callback.answer('У вас пока нет инструментов с отзывами.', show_alert=True)
        else:
            await callback.message.edit_text(
                'Инструменты, к которым оставлен отзыв:', 
                reply_markup=await review_tools(reviews, session_instance)
            )
        await callback.answer()

@router.callback_query(F.data == 'remove_from_review')
async def remove_from_review(callback: CallbackQuery):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        if not tm.tool_id:
            await callback.answer("Не удалось определить инструмент", show_alert=True)
            return
        
        rr = ReviewRepository(session_instance)
        await rr.delete(user.id, tm.tool_id)
        
        await callback.answer("Отзыв удалён!", show_alert=True)

        if tm.message_id:
            try:
                await callback.bot.edit_message_reply_markup(
                    chat_id=tm.chat_id,
                    message_id=tm.message_id,
                    reply_markup=await get_tool_keyboard(callback.from_user.id, tm.tool_id, session_instance)
                )
            except Exception:
                pass

@router.callback_query(F.data == 'update_review')
async def update_review(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(callback.from_user.id)

        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return

        if not tm.tool_id:
            await callback.answer("Не удалось определить инструмент", show_alert=True)
            return

        await state.set_state(Reviews.waiting_for_text)
        await state.update_data(tool_id=tm.tool_id)

        await callback.answer("Введите новый текст отзыва:")
        await callback.message.answer("Введите новый текст отзыва:", reply_markup=cancel_keyboard)