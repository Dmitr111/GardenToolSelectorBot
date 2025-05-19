from aiogram import F, Router
from aiogram.types import CallbackQuery
from ...database.db import async_session as session
from ...database.repositories import ToolRepository, ReviewRepository
from ...keyboards.admin.review_keyboards import *

router = Router()

@router.callback_query(F.data == 'view_tool_reviews')
async def view_tool_reviews(callback: CallbackQuery):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tools = await tr.get_all()

        if not tools:
            await callback.answer("Нет доступных инструментов с отзывами.")
            return

        await callback.message.edit_text("Выберите инструмент для просмотра отзывов:", 
                                        reply_markup=await build_tools_keyboard(tools))
    await callback.answer()

@router.callback_query(F.data.startswith('select_tool_'))
async def select_tool(callback: CallbackQuery):
    tool_id = int(callback.data.split('_')[2])
    async with session() as session_instance:
        rr = ReviewRepository(session_instance)
        reviews = await rr.get_all_for_tool(tool_id)

        if not reviews:
            await callback.answer("Нет отзывов на данный инструмент.")
            return

        await callback.message.edit_text("Выберите пользователя, оставившего отзыв:", 
                                        reply_markup=await build_reviews_keyboard(reviews, session_instance))
    await callback.answer()

@router.callback_query(F.data.startswith('select_review_'))
async def show_selected_review(callback: CallbackQuery):
    review_id = int(callback.data.split('_')[2])
    async with session() as session_instance:
        rr = ReviewRepository(session_instance)
        review = await rr.get_by_id(review_id)

        ur = UserRepository(session_instance)
        user = await ur.get_by_id(user_id=review.user_id)

        tr = ToolRepository(session_instance)
        tool = await tr.get_by_id(review.tool_id)

        if not review:
            await callback.answer("Отзыв не найден")
            return

        review_text = (
            f"Отзыв пользователя {user.username} ({user.telegram_id}) об инструменте {tool.name}:\n\n"
            f"💬 {review.text}\n"
            f"⭐ Рейтинг: {review.rating}"
        )
        await callback.message.edit_text(review_text, reply_markup=await build_review_actions_keyboard(review_id))
    await callback.answer()

@router.callback_query(F.data.startswith('delete_review_'))
async def delete_review(callback: CallbackQuery):
    review_id = int(callback.data.split('_')[2])
    async with session() as session_instance:
        rr = ReviewRepository(session_instance)
        review = await rr.get_by_id(review_id)
        user_id = review.user.telegram_id

        if not review:
            await callback.answer("Отзыв не найден")
            return

        await rr.delete_by_id(review_id)
        await callback.message.edit_text("Отзыв успешно удален!")
        await callback.bot.send_message(chat_id=user_id, text="Ваш отзыв был удален администратором.")
    await callback.answer()