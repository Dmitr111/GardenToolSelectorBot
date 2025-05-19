from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..states import AdminRecommendations
from ...database.db import async_session as session
from ...database.repositories import RecommendationRepository, ProficiencyLevelRepository, CategoryRepository
from ...keyboards.common_keyboards import *
from ...keyboards.admin.recommendations_keyboards import *
from ...keyboards.admin.proficiency_levels_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_recommendations')
async def manage_recommendations(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление рекомендациями:",
        reply_markup=manage_recommendations_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'add_recommendation')
async def add_recommendation_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        plr = ProficiencyLevelRepository(session_instance)
        levels = await plr.get_all()
        
        if not levels:
            await callback.answer("Нет доступных уровней владения")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_proficiency_level)
        await callback.message.edit_text(
            "Выберите уровень владения для рекомендации:",
            reply_markup=await proficiency_levels_select_keyboard(levels)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('selectlevel_'), AdminRecommendations.waiting_for_recommendation_proficiency_level)
async def select_recommendation_level(callback: CallbackQuery, state: FSMContext):
    level_id = int(callback.data.split('_')[1])
    await state.update_data(proficiency_level_id=level_id)
    
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        
        if not categories:
            await callback.answer("Нет доступных категорий")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_category)
        await callback.message.edit_text(
            "Выберите категорию для рекомендации:",
            reply_markup=await categories_select_keyboard(categories)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('selectcat_'), AdminRecommendations.waiting_for_recommendation_category)
async def select_recommendation_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])
    await state.update_data(category_id=category_id)
    await state.set_state(AdminRecommendations.waiting_for_recommendation_text)
    
    await callback.message.edit_text(
        "Введите текст рекомендации (макс. 1024 символа):",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@router.message(AdminRecommendations.waiting_for_recommendation_text)
async def add_recommendation_text(message: Message, state: FSMContext):
    if len(message.text) > 1024:
        await message.answer("Текст слишком длинный (макс. 1024 символа). Попробуйте еще раз.")
        return
    
    data = await state.get_data()
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendation = await rr.create(
            proficiency_level_id=data['proficiency_level_id'],
            category_id=data['category_id'],
            text=message.text
        )
        
        plr = ProficiencyLevelRepository(session_instance)
        level = await plr.get_by_id(recommendation.proficiency_level_id)
        cr = CategoryRepository(session_instance)
        category = await cr.get_by_id(recommendation.category_id)
        
        await message.answer(
            f"Рекомендация успешно добавлена!\n\n"
            f"Уровень: {level.name}\n"
            f"Категория: {category.name}\n"
            f"Текст: {recommendation.text}",
            reply_markup=add_another_recommendation_keyboard
        )
        await state.clear()

@router.callback_query(F.data == 'edit_recommendation')
async def edit_recommendation_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendations = await rr.get_all_with_details()
        
        if not recommendations:
            await callback.answer("Нет доступных рекомендаций для редактирования")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit)
        await callback.message.edit_text(
            "Выберите рекомендацию для редактирования:",
            reply_markup=await recommendations_edit_keyboard(recommendations)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('editrec_'), AdminRecommendations.waiting_for_recommendation_edit)
async def edit_recommendation_selected(callback: CallbackQuery, state: FSMContext):
    recommendation_id = int(callback.data.split('_')[1])
    await state.update_data(recommendation_id=recommendation_id)
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendation = await rr.get_with_details(recommendation_id)
        
        await callback.message.edit_text(
            f"Текущие данные рекомендации:\n\n"
            f"Уровень: {recommendation.proficiency_level.name}\n"
            f"Категория: {recommendation.category.name}\n"
            f"Текст: {recommendation.text}\n\n"
            "Что вы хотите изменить?",
            reply_markup=edit_recommendation_options_keyboard
        )
    await callback.answer()

@router.callback_query(F.data == 'edit_recommendation_level')
async def edit_recommendation_level_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        plr = ProficiencyLevelRepository(session_instance)
        levels = await plr.get_all()
        
        if not levels:
            await callback.answer("Нет доступных уровней владения")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit_proficiency_level)
        await callback.message.edit_text(
            "Выберите новый уровень владения:",
            reply_markup=await proficiency_levels_select_keyboard(levels)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('selectlevel_'), AdminRecommendations.waiting_for_recommendation_edit_proficiency_level)
async def edit_recommendation_level_select(callback: CallbackQuery, state: FSMContext):
    level_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    recommendation_id = data['recommendation_id']
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        await rr.update(recommendation_id, proficiency_level_id=level_id)
        recommendation = await rr.get_with_details(recommendation_id)
        
        await callback.message.edit_text(
            f"Рекомендация успешно обновлена!\n\n"
            f"Уровень: {recommendation.proficiency_level.name}\n"
            f"Категория: {recommendation.category.name}\n"
            f"Текст: {recommendation.text}",
            reply_markup=edit_recommendation_options_keyboard
        )
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit)
    await callback.answer()

@router.callback_query(F.data == 'edit_recommendation_category')
async def edit_recommendation_category_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        
        if not categories:
            await callback.answer("Нет доступных категорий")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit_category)
        await callback.message.edit_text(
            "Выберите новую категорию:",
            reply_markup=await categories_select_keyboard(categories)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('selectcat_'), AdminRecommendations.waiting_for_recommendation_edit_category)
async def edit_recommendation_category_select(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    recommendation_id = data['recommendation_id']
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        await rr.update(recommendation_id, category_id=category_id)
        recommendation = await rr.get_with_details(recommendation_id)
        
        await callback.message.edit_text(
            f"Рекомендация успешно обновлена!\n\n"
            f"Уровень: {recommendation.proficiency_level.name}\n"
            f"Категория: {recommendation.category.name}\n"
            f"Текст: {recommendation.text}",
            reply_markup=edit_recommendation_options_keyboard
        )
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit)
    await callback.answer()

@router.callback_query(F.data == 'edit_recommendation_text')
async def edit_recommendation_text_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminRecommendations.waiting_for_recommendation_edit_text)
    await callback.message.edit_text(
        "Введите новый текст рекомендации:",
        reply_markup=cancel_keyboard
    )
    await callback.answer()

@router.message(AdminRecommendations.waiting_for_recommendation_edit_text)
async def edit_recommendation_text_process(message: Message, state: FSMContext):
    if len(message.text) > 1024:
        await message.answer("Текст слишком длинный (макс. 1024 символа). Попробуйте еще раз.")
        return
    
    data = await state.get_data()
    recommendation_id = data['recommendation_id']
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        await rr.update(recommendation_id, text=message.text)
        recommendation = await rr.get_with_details(recommendation_id)
        
        await message.answer(
            f"Рекомендация успешно обновлена!\n\n"
            f"Уровень: {recommendation.proficiency_level.name}\n"
            f"Категория: {recommendation.category.name}\n"
            f"Текст: {recommendation.text}",
            reply_markup=edit_recommendation_options_keyboard
        )
        await state.set_state(AdminRecommendations.waiting_for_recommendation_edit)

@router.callback_query(F.data == 'delete_recommendation')
async def delete_recommendation_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendations = await rr.get_all_with_details()
        
        if not recommendations:
            await callback.answer("Нет доступных рекомендаций для удаления")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_delete)
        await callback.message.edit_text(
            "Выберите рекомендацию для удаления:",
            reply_markup=await recommendations_delete_keyboard(recommendations)
        )
    await callback.answer()

@router.callback_query(F.data.startswith('delrec_'), AdminRecommendations.waiting_for_recommendation_delete)
async def delete_recommendation_confirm(callback: CallbackQuery, state: FSMContext):
    recommendation_id = int(callback.data.split('_')[1])
    await state.update_data(recommendation_id=recommendation_id)
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendation = await rr.get_with_details(recommendation_id)
        
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить рекомендацию?\n\n"
            f"Уровень: {recommendation.proficiency_level.name}\n"
            f"Категория: {recommendation.category.name}\n"
            f"Текст: {recommendation.text}",
            reply_markup=confirm_delete_keyboard
        )
    await callback.answer()

@router.callback_query(F.data == 'confirm_delete', AdminRecommendations.waiting_for_recommendation_delete)
async def delete_recommendation_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    recommendation_id = data.get('recommendation_id')
    
    async with session() as session_instance:
        rr = RecommendationRepository(session_instance)
        recommendation = await rr.get_with_details(recommendation_id)
        
        if recommendation:
            await rr.delete(recommendation_id)
            await callback.message.edit_text(
                f"Рекомендация для уровня '{recommendation.proficiency_level.name}' "
                f"и категории '{recommendation.category.name}' успешно удалена!",
                reply_markup=back_to_recommendations_keyboard
            )
        else:
            await callback.answer("Рекомендация не найдена")
    
    await state.clear()

@router.callback_query(F.data == 'back_to_recommendations')
async def back_to_recommendations(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Управление рекомендациями:",
        reply_markup=manage_recommendations_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'add_another_recommendation')
async def add_another_recommendation(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        plr = ProficiencyLevelRepository(session_instance)
        levels = await plr.get_all()
        
        if not levels:
            await callback.answer("Нет доступных уровней владения")
            return
        
        await state.set_state(AdminRecommendations.waiting_for_recommendation_proficiency_level)
        await callback.message.edit_text(
            "Выберите уровень владения для рекомендации:",
            reply_markup=await proficiency_levels_select_keyboard(levels)
        )
    await callback.answer()