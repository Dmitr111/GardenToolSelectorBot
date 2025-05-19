from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..states import AdminCategories
from ...database.db import async_session as session
from ...database.repositories import CategoryRepository
from ...keyboards.admin.categories_keyboards import *
from ...keyboards.common_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_categories')
async def manage_categories(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление категориями:",
        reply_markup = manage_categories_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'add_category')
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategories.waiting_for_category_name)
    await callback.message.edit_text(
        "Введите название новой категории:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.message(AdminCategories.waiting_for_category_name)
async def add_category_name(message: Message, state: FSMContext):
    if len(message.text) > 90:
        await message.answer("Название слишком длинное (макс. 90 символов). Попробуйте еще раз.")
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AdminCategories.waiting_for_category_description)
    await message.answer(
        "Введите описание категории (необязательно):",
        reply_markup = skip_keyboard
    )

@router.message(AdminCategories.waiting_for_category_description)
async def add_category_description(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 1024:
            await message.answer("Описание слишком длинное (макс. 1024 символа). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        name = data['name']
        description = message.text.strip()
        
        try:
            cr = CategoryRepository(session_instance)
            await cr.create(name, description)

            await message.answer(f"Категория '{name}' успешно добавлена!", reply_markup = add_another_category_keyboard)
        except Exception as e:
            await message.answer(
                f"Ошибка при добавлении категории: {str(e)}",
                reply_markup =  back_to_categories_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'skip', AdminCategories.waiting_for_category_description)
async def skip_category_description(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        name = data['name']
        
        try:
            
            cr = CategoryRepository(session_instance)
            await cr.create(name, None)

            await callback.message.edit_text(
                f"Категория '{name}' успешно добавлена без описания!",
                reply_markup = add_another_category_keyboard
            )
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при добавлении категории: {str(e)}",
                reply_markup =  back_to_categories_keyboard
            )
        
        await state.clear()
        await callback.answer()

@router.callback_query(F.data == 'add_another_category')
async def add_another_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategories.waiting_for_category_name)
    await callback.message.edit_text(
        "Введите название новой категории:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'edit_category')
async def edit_category_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()

        if not categories:
            await callback.answer("Нет доступных категорий для редактирования")
            return
        
        await state.set_state(AdminCategories.waiting_for_category_edit)
        await callback.message.edit_text(
            "Выберите категорию для редактирования:",
            reply_markup = await categories_edit_keyboard(categories)
        )
        await callback.answer()

@router.callback_query(F.data.startswith('editcat_'), AdminCategories.waiting_for_category_edit)
async def edit_category_selected(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        category_id = int(callback.data.split('_')[1])
        cr = CategoryRepository(session_instance)
        category = await cr.get_all(category_id)
    
        if not category:
            await callback.answer("Категория не найдена")
            return
        
        await state.update_data(category_id=category_id)
        await callback.message.edit_text(
            f"Текущие данные категории:\n\n"
            f"Название: {category.name}\n"
            f"Описание: {category.description or 'Отсутствует'}\n\n"
            "Что вы хотите изменить?",
            reply_markup = edit_category_options_keyboard
        )
        await callback.answer()

@router.callback_query(F.data == 'edit_category_name')
async def edit_category_name_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategories.waiting_for_category_edit_name)
    await callback.message.edit_text(
        "Введите новое название категории:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.message(AdminCategories.waiting_for_category_edit_name)
async def edit_category_name_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 90:
            await message.answer("Название слишком длинное (макс. 90 символов). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        category_id = data['category_id']
        
        try:

            cr = CategoryRepository(session_instance)
            category = await cr.update(category_id, name=message.text)

            await message.answer(
                f"Название категории успешно обновлено!\n\n"
                f"Новые данные:\n"
                f"Название: {category.name}\n"
                f"Описание: {category.description or 'Отсутствует'}",
                reply_markup = edit_category_options_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении категории: {str(e)}",
                reply_markup =  back_to_categories_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'edit_category_description')
async def edit_category_description_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminCategories.waiting_for_category_edit_description)
    await callback.message.edit_text(
        "Введите новое описание категории (или отправьте 'удалить' чтобы очистить текущее):",
        reply_markup = skip_keyboard
    )
    await callback.answer()

@router.message(AdminCategories.waiting_for_category_edit_description)
async def edit_category_description_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 1024:
            await message.answer("Описание слишком длинное (макс. 1024 символа). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        category_id = data['category_id']
        description = None if message.text.lower() == 'удалить' else message.text
        
        try:
            cr = CategoryRepository(session_instance)
            await cr.update(category_id, description=description)
            category = await cr.get_by_id(category_id)

            await message.answer(
                f"Описание категории успешно обновлено!\n\n"
                f"Новые данные:\n"
                f"Название: {category.name}\n"
                f"Описание: {category.description or 'Отсутствует'}",
                reply_markup = back_to_categories_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении категории: {str(e)}",
                reply_markup =  back_to_categories_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'delete_category')
async def delete_category_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()

        if not categories:
            await callback.answer("Нет доступных категорий для удаления")
            return
        
        await state.set_state(AdminCategories.waiting_for_category_delete)
        await callback.message.edit_text(
            "Выберите категорию для удаления:",
            reply_markup = await categories_delete_keyboard(categories)
        )
        await callback.answer()

@router.callback_query(F.data.startswith('deletecat_'), AdminCategories.waiting_for_category_delete)
async def delete_category_confirm(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        category_id = int(callback.data.split('_')[1])
        cr = CategoryRepository(session_instance)
        category = await cr.get_by_id(category_id)
    
        if not category:
            await callback.answer("Категория не найдена")
            return
        
        await state.update_data(category_id=category_id)
        tools_count = await cr.get_tools_count(category_id)
        
        if tools_count > 0:
            await callback.message.edit_text(
                f"⚠️ Внимание! В категории '{category.name}' есть {tools_count} инструментов.\n"
                "При удалении категории все связанные инструменты также будут удалены.\n"
                "Вы уверены, что хотите удалить эту категорию?",
                reply_markup = confirm_delete_keyboard
            )
        else:
            await callback.message.edit_text(
                f"Вы уверены, что хотите удалить категорию '{category.name}'?",
                reply_markup = confirm_delete_keyboard
            )
        
        await callback.answer()

@router.callback_query(F.data == 'confirm_delete', AdminCategories.waiting_for_category_delete)
async def delete_category_final(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        category_id = data.get('category_id')
        
        if not category_id:
            await callback.answer("Ошибка: категория не выбрана")
            return
        
        try:
            cr = CategoryRepository(session_instance)
            category = await cr.get_by_id(category_id)
                
            if category:
                await cr.delete(category_id)
                await callback.message.edit_text(f"Категория '{category.name}' успешно удалена!")
            else:
                await callback.answer("Категория не найдена")
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при удалении категории: {str(e)}",
                reply_markup = back_to_categories_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'cancel_delete')
async def cancel_delete_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Удаление отменено.",
        reply_markup = manage_categories_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'back_to_categories')
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Управление категориями:",
        reply_markup = manage_categories_keyboard
    )
    await callback.answer()