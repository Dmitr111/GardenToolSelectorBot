from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..states import AdminManufacturers
from ...database.db import async_session as session
from ...database.repositories import ManufacturerRepository
from ...keyboards.common_keyboards import *
from ...keyboards.admin.manufacturers_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_manufacturers')
async def manage_manufacturers(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление производителями:",
        reply_markup = manage_manufacturers_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'add_manufacturer')
async def add_manufacturer_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_name)
    await callback.message.edit_text(
        "Введите название нового производителя:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.message(AdminManufacturers.waiting_for_manufacturer_name)
async def add_manufacturer_name(message: Message, state: FSMContext):
    if len(message.text) > 90:
        await message.answer("Название слишком длинное (макс. 90 символов). Попробуйте еще раз.")
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_country)
    await message.answer(
        "Введите страну производителя (необязательно):",
        reply_markup = skip_keyboard
    )

@router.message(AdminManufacturers.waiting_for_manufacturer_country)
async def add_manufacturer_country(message: Message, state: FSMContext):
    if len(message.text) > 56:
        await message.answer("Название страны слишком длинное (макс. 56 символов). Попробуйте еще раз.")
        return
    
    country = message.text
    await state.update_data(country=country)
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_website)
    await message.answer(
        "Введите веб-сайт производителя (необязательно):",
        reply_markup = skip_keyboard
    )

@router.message(AdminManufacturers.waiting_for_manufacturer_website)
async def add_manufacturer_website(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 255:
            await message.answer("Ссылка слишком длинная (макс. 255 символов). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        website = message.text
        
        try:
            
            mr = ManufacturerRepository(session_instance)
            await mr.create(data['name'], data['country'], website)

            await message.answer(
                f"Производитель '{data['name']}' успешно добавлен!",
                reply_markup = add_another_manufacturer_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при добавлении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'skip', AdminManufacturers.waiting_for_manufacturer_country)
async def skip_manufacturer_country(callback: CallbackQuery, state: FSMContext):
    await state.update_data(country=None)
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_website)
    await callback.message.edit_text(
        "Введите веб-сайт производителя (необязательно):",
        reply_markup = skip_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'skip', AdminManufacturers.waiting_for_manufacturer_website)
async def skip_manufacturer_website(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        
        try:
            mr = ManufacturerRepository(session_instance)
            await mr.create(data['name'], data['country'], None)

            await callback.message.edit_text(
                f"Производитель '{data['name']}' успешно добавлен!",
                reply_markup = add_another_manufacturer_keyboard
            )
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при добавлении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()
        await callback.answer()

@router.callback_query(F.data == 'add_another_manufacturer')
async def add_another_manufacturer(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_name)
    await callback.message.edit_text(
        "Введите название нового производителя:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'edit_manufacturer')
async def edit_manufacturer_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        mr = ManufacturerRepository(session_instance)
        manufacturers = await mr.get_all()

        if not manufacturers:
            await callback.answer("Нет доступных производителей для редактирования")
            return
        
        await state.set_state(AdminManufacturers.waiting_for_manufacturer_edit)
        await callback.message.edit_text(
            "Выберите производителя для редактирования:",
            reply_markup = await manufacturers_edit_keyboard(manufacturers)
        )
        await callback.answer()

@router.callback_query(F.data.startswith('editmanuf_'), AdminManufacturers.waiting_for_manufacturer_edit)
async def edit_manufacturer_selected(callback: CallbackQuery, state: FSMContext):
    manufacturer_id = int(callback.data.split('_')[1])
    async with session() as session_instance:
        mr = ManufacturerRepository(session_instance)
        manufacturer = await mr.get_by_id(manufacturer_id)
    
        if not manufacturer:
            await callback.answer("Производитель не найден")
            return
        
        await state.update_data(manufacturer_id=manufacturer_id)
        await callback.message.edit_text(
            f"Текущие данные производителя:\n\n"
            f"Название: {manufacturer.name}\n"
            f"Страна: {manufacturer.country or 'Отсутствует'}\n"
            f"Веб-сайт: {manufacturer.website or 'Отсутствует'}\n\n"
            "Что вы хотите изменить?",
            reply_markup = edit_manufacturer_options_keyboard
        )
        await callback.answer()

@router.callback_query(F.data == 'edit_manufacturer_name')
async def edit_manufacturer_name_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_edit_name)
    await callback.message.edit_text(
        "Введите новое название производителя:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.message(AdminManufacturers.waiting_for_manufacturer_edit_name)
async def edit_manufacturer_name_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 90:
            await message.answer("Название слишком длинное (макс. 90 символов). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        manufacturer_id = data['manufacturer_id']
        
        try:
            mr = ManufacturerRepository(session_instance)
            await mr.update(manufacturer_id, name=message.text)
            manufacturer = await mr.get_by_id(manufacturer_id)

            await message.answer(
                f"Название производителя успешно обновлено!\n\n"
                f"Новые данные:\n"
                f"Название: {manufacturer.name}\n"
                f"Страна: {manufacturer.country or 'Отсутствует'}\n"
                f"Веб-сайт: {manufacturer.website or 'Отсутствует'}",
                reply_markup = edit_manufacturer_options_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'edit_manufacturer_country')
async def edit_manufacturer_country_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_edit_country)
    await callback.message.edit_text(
        "Введите новую страну производителя (или отправьте 'удалить' чтобы очистить текущее):",
        reply_markup = skip_keyboard
    )
    await callback.answer()

@router.message(AdminManufacturers.waiting_for_manufacturer_edit_country)
async def edit_manufacturer_country_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 56:
            await message.answer("Название страны слишком длинное (макс. 56 символов). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        manufacturer_id = data['manufacturer_id']
        country = None if message.text.lower() == 'удалить' else message.text
        
        try:
            mr = ManufacturerRepository(session_instance)
            await mr.update(manufacturer_id, country=country)
            manufacturer = await mr.get_by_id(manufacturer_id)

            await message.answer(
                f"Страна производителя успешно обновлена!\n\n"
                f"Новые данные:\n"
                f"Название: {manufacturer.name}\n"
                f"Страна: {manufacturer.country or 'неизвестно'}\n"
                f"Веб-сайт: {manufacturer.website or 'неизвестно'}",
                reply_markup = edit_manufacturer_options_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'edit_manufacturer_website')
async def edit_manufacturer_website_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminManufacturers.waiting_for_manufacturer_edit_website)
    await callback.message.edit_text(
        "Введите новый веб-сайт производителя (или отправьте 'удалить' чтобы очистить текущее):",
        reply_markup = skip_keyboard
    )
    await callback.answer()

@router.message(AdminManufacturers.waiting_for_manufacturer_edit_website)
async def edit_manufacturer_website_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 255:
            await message.answer("Ссылка слишком длинная (макс. 255 символов). Попробуйте еще раз.")
            return
        
        data = await state.get_data()
        manufacturer_id = data['manufacturer_id']
        website = None if message.text.lower() == 'удалить' else message.text
        
        try:
            mr = ManufacturerRepository(session_instance)
            await mr.update(manufacturer_id, website=website)
            manufacturer = await mr.get_by_id(manufacturer_id)

            await message.answer(
                f"Веб-сайт производителя успешно обновлен!\n\n"
                f"Новые данные:\n"
                f"Название: {manufacturer.name}\n"
                f"Страна: {manufacturer.country or 'Отсутствует'}\n"
                f"Веб-сайт: {manufacturer.website or 'Отсутствует'}",
                reply_markup = edit_manufacturer_options_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'delete_manufacturer')
async def delete_manufacturer_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        mr = ManufacturerRepository(session_instance)
        manufacturers = await mr.get_all()
    
        if not manufacturers:
            await callback.answer("Нет доступных производителей для удаления")
            return
        
        await state.set_state(AdminManufacturers.waiting_for_manufacturer_delete)
        await callback.message.edit_text(
            "Выберите производителя для удаления:",
            reply_markup = await manufacturers_delete_keyboard(manufacturers)
        )
        await callback.answer()

@router.callback_query(F.data.startswith('deletemanuf_'), AdminManufacturers.waiting_for_manufacturer_delete)
async def delete_manufacturer_confirm(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        manufacturer_id = int(callback.data.split('_')[1])
        mr = ManufacturerRepository(session_instance)
        manufacturer = await mr.get_by_id(manufacturer_id)
    
        if not manufacturer:
            await callback.answer("Производитель не найден")
            return
    
        await state.update_data(manufacturer_id=manufacturer_id)
        tools_count = await mr.get_tools_count(manufacturer_id)
    
        if tools_count > 0:
            await callback.message.edit_text(
                f"⚠️ Внимание! У производителя '{manufacturer.name}' есть {tools_count} инструментов.\n"
                "При удалении производителя все связанные инструменты также будут удалены.\n"
                "Вы уверены, что хотите удалить этого производителя?",
                reply_markup = confirm_delete_keyboard
            )
        else:
            await callback.message.edit_text(
                f"Вы уверены, что хотите удалить производителя '{manufacturer.name}'?",
                reply_markup = confirm_delete_keyboard
            )
    
        await callback.answer()

@router.callback_query(F.data == 'confirm_delete', AdminManufacturers.waiting_for_manufacturer_delete)
async def delete_manufacturer_final(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        manufacturer_id = data.get('manufacturer_id')
        
        if not manufacturer_id:
            await callback.answer("Ошибка: производитель не выбран")
            return
        
        try:
            mr = ManufacturerRepository(session_instance)
            manufacturer = await mr.get_by_id(manufacturer_id)

            if manufacturer:
                await mr.delete(manufacturer_id)
                await callback.message.edit_text(f"Производитель '{manufacturer.name}' успешно удален!")
            else:
                await callback.answer("Производитель не найдена")
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при удалении производителя: {str(e)}",
                reply_markup = back_to_manufacturer_keyboard
            )
        
        await state.clear()

@router.callback_query(F.data == 'cancel_delete', AdminManufacturers.waiting_for_manufacturer_delete)
async def cancel_delete_manufacturer(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Удаление отменено.",
        reply_markup = manage_manufacturers_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'back_to_manufacturers')
async def back_to_manufacturers(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Управление производителями:",
        reply_markup = manage_manufacturers_keyboard
    )
    await callback.answer()