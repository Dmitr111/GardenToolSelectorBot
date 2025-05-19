from decimal import Decimal
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from ..states import AdminTools
from ...database.db import async_session as session
from ...database.repositories import *
from ..utils import tool_message as tm
from ...keyboards.common_keyboards import *
from ...keyboards.selection_keyboards import *
from ...keyboards.admin.tools_keyboards import *

router = Router()

@router.callback_query(F.data == 'manage_tools')
async def manage_tools(callback: CallbackQuery):
    await callback.message.edit_text(
        "Управление инструментами:",
        reply_markup = manage_tools_keyboard
    )
    await callback.answer()

@router.callback_query(F.data == 'add_tool')
async def add_tool_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_name)
    await callback.message.edit_text(
        "Введите название нового инструмента:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()

@router.message(AdminTools.waiting_for_tool_name)
async def add_tool_name(message: Message, state: FSMContext):
    if len(message.text) > 60:
        await message.answer("Название слишком длинное (макс. 60 символов). Попробуйте еще раз.")
        return
    
    await state.update_data(name=message.text)
    await state.set_state(AdminTools.waiting_for_tool_model)
    await message.answer(
        "Введите модель инструмента:",
        reply_markup = cancel_keyboard
    )

@router.message(AdminTools.waiting_for_tool_model)
async def add_tool_model(message: Message, state: FSMContext):
    if message.text != "Пропустить":
        if len(message.text) > 60:
            await message.answer("Модель слишком длинная (макс. 60 символов). Попробуйте еще раз.")
            return
        await state.update_data(model=message.text)
    else:
        await state.update_data(model=None)
    
    await state.set_state(AdminTools.waiting_for_tool_description)
    await message.answer(
        "Введите описание инструмента (необязательно):",
        reply_markup = skip_keyboard
    )


@router.message(AdminTools.waiting_for_tool_description)
async def add_tool_description(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 1024:
            await message.answer("Описание слишком длинное (макс. 1024 символа). Попробуйте еще раз.")
            return
        
        description = message.text
        await state.update_data(description=description)
        await state.set_state(AdminTools.waiting_for_tool_category)
        
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        if not categories:
            await message.answer("Нет доступных категорий. Сначала создайте категорию.")
            await state.clear()
            return
        
        await message.answer(
            "Выберите категорию инструмента:",
            reply_markup = await categories_select_keyboard(categories)
        )


@router.callback_query(F.data.startswith('selectcat_'), AdminTools.waiting_for_tool_category)
async def select_tool_category(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        category_id = int(callback.data.split('_')[1])
        await state.update_data(category_id=category_id)
        await state.set_state(AdminTools.waiting_for_tool_manufacturer)
        
        mr = ManufacturerRepository(session_instance)
        manufacturers = await mr.get_all()
        if not manufacturers:
            await callback.message.answer("Нет доступных производителей. Сначала создайте производителя.")
            await state.clear()
            return
        
        await callback.message.edit_text(
            "Выберите производителя инструмента:",
            reply_markup = await manufacturers_select_keyboard(manufacturers)
        )
        await callback.answer()


@router.callback_query(F.data.startswith('selectmanuf_'), AdminTools.waiting_for_tool_manufacturer)
async def select_tool_manufacturer(callback: CallbackQuery, state: FSMContext):
    manufacturer_id = int(callback.data.split('_')[1])
    await state.update_data(manufacturer_id=manufacturer_id)
    
    async with session() as session_instance:
        mr = MaterialRepository(session_instance)
        materials = await mr.get_all()
        
        if materials:
            await state.set_state(AdminTools.waiting_for_tool_materials_select)
            await callback.message.edit_text(
                "Выберите материалы инструмента:",
                reply_markup=await materials_select_keyboard(materials, multi_select=True)
            )
        else:
            await state.update_data(materials=[])
            await state.set_state(AdminTools.waiting_for_tool_weight)
            await callback.message.edit_text(
                "Нет доступных материалов. Введите вес инструмента в кг (необязательно):",
                reply_markup=skip_keyboard
            )
    
    await callback.answer()


@router.callback_query(F.data.startswith('selectmaterial_'), AdminTools.waiting_for_tool_materials_select)
async def select_tool_materials(callback: CallbackQuery, state: FSMContext):
    material_id = int(callback.data.split('_')[1])
    
    async with session() as session_instance:
        # Получаем текущий список выбранных материалов
        data = await state.get_data()
        selected_materials = data.get('materials', [])
        
        # Добавляем или удаляем материал
        if material_id in selected_materials:
            selected_materials.remove(material_id)
        else:
            selected_materials.append(material_id)
        
        await state.update_data(materials=selected_materials)
        
        # Обновляем клавиатуру с отметкой выбранных материалов
        mr = MaterialRepository(session_instance)
        materials = await mr.get_all()
        await callback.message.edit_reply_markup(
            reply_markup=await materials_select_keyboard(materials, selected_materials, multi_select=True)
        )
    
    await callback.answer()


@router.callback_query(F.data == 'no_materials_selected')
async def no_materials_selected(callback: CallbackQuery):
    await callback.answer("Пожалуйста, выберите хотя бы один материал", show_alert=True)


@router.callback_query(F.data == 'confirm_materials', AdminTools.waiting_for_tool_materials_select)
async def confirm_tool_materials(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_weight)
    await callback.message.edit_text(
        "Введите вес инструмента в кг (необязательно):",
        reply_markup=skip_keyboard
    )
    await callback.answer()


@router.message(AdminTools.waiting_for_tool_weight)
async def add_tool_weight(message: Message, state: FSMContext):
    try:
        weight = Decimal(message.text.replace(',', '.'))
        if weight <= 0:
            raise ValueError
        await state.update_data(weight=weight)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для веса (например: 1.5)")
        return
    
    await state.set_state(AdminTools.waiting_for_tool_price)
    await message.answer(
        "Введите диапазон цену инструмента (необязательно, например: 199.00):",
        reply_markup = skip_keyboard
    )


@router.message(AdminTools.waiting_for_tool_price)
async def add_tool_price(message: Message, state: FSMContext):
    try:
        price = Decimal(message.text.replace(',', '.'))
        if price <= 0:
            raise ValueError
        await state.update_data(price=price)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для цены (например: 199.00)")
        return
    
    await state.set_state(AdminTools.waiting_for_tool_images)
    await message.answer(
        "Отправьте URL изображения инструмента (необязательно, макс. 500 символов):",
        reply_markup = skip_keyboard
    )


@router.message(AdminTools.waiting_for_tool_images)
async def add_tool_images(message: Message, state: FSMContext):
    async with session() as session_instance:
        if len(message.text) > 500:
            await message.answer("Ссылка слишком длинная (макс. 500 символов). Попробуйте еще раз.")
            return
        
        image_url = message.text if message.text != "Пропустить" else None
        data = await state.get_data()
        
        try:
            tr = ToolRepository(session_instance)
            tmr= ToolMaterialRepository(session_instance)
            
            tool = await tr.create(
                name=data['name'],
                model=data.get('model'),
                description=data.get('description'),
                category_id=data['category_id'],
                manufacturer_id=data['manufacturer_id'],
                weight=data.get('weight'),
                price=data.get('price'),
                image_url=image_url
            )
            
            if 'materials' in data and data['materials']:
                for material_id in data['materials']:
                    await tmr.create(tool.id, material_id)
            
            await message.answer(
                f"Инструмент '{data['name']}' успешно добавлен!",
                reply_markup=add_another_tool_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при добавлении инструмента: {str(e)}",
                reply_markup=back_to_tools_keyboard
            )
        
        await state.clear()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_model)
async def skip_tool_description(callback: CallbackQuery, state: FSMContext):
    await state.update_data(model=None)
    await state.set_state(AdminTools.waiting_for_tool_description)
    
    await callback.message.edit_text(
        "Введите описание инстурмента (необязательно):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_description)
async def skip_tool_description(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        await state.update_data(description=None)
        await state.set_state(AdminTools.waiting_for_tool_category)
        
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        if not categories:
            await callback.message.edit_text("Нет доступных категорий. Сначала создайте категорию.")
            await state.clear()
            return
        
        await callback.message.edit_text(
            "Выберите категорию инструмента:",
            reply_markup = await categories_select_keyboard(categories)
        )
        await callback.answer()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_materials_select)
async def skip_tool_materials(callback: CallbackQuery, state: FSMContext):
    await state.update_data(materials=[])
    await state.set_state(AdminTools.waiting_for_tool_weight)
    await callback.message.edit_text(
        "Введите вес инструмента в кг (необязательно):",
        reply_markup=skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_weight)
async def skip_tool_weight(callback: CallbackQuery, state: FSMContext):
    await state.update_data(weight=None)
    await state.set_state(AdminTools.waiting_for_tool_price)
    await callback.message.edit_text(
        "Введите диапазон цену инструмента (необязательно, например: 199.00):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_price)
async def skip_tool_price(callback: CallbackQuery, state: FSMContext):
    await state.update_data(price=None)
    await state.set_state(AdminTools.waiting_for_tool_images)
    await callback.message.edit_text(
        "Отправьте URL изображений инструмента через запятую (необязательно, макс. 500 символов):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'skip', AdminTools.waiting_for_tool_images)
async def skip_tool_images(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        
        try:
            tr = ToolRepository(session_instance)
            tmr= ToolMaterialRepository(session_instance)
            
            tool = await tr.create(
                name=data['name'],
                model=data.get('model'),
                description=data.get('description'),
                category_id=data['category_id'],
                manufacturer_id=data['manufacturer_id'],
                weight=data.get('weight'),
                price=data.get('price'),
                image_url=None
            )
            
            selected_materials = data.get('materials', [])
            for material_id in selected_materials:
                await tmr.create(tool.id, material_id)

            await callback.message.edit_text(
                f"Инструмент '{data['name']}' успешно добавлен!",
                reply_markup=add_another_tool_keyboard
            )
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при добавлении инструмента: {str(e)}",
                reply_markup=back_to_tools_keyboard
            )
        
        await state.clear()
        await callback.answer()


@router.callback_query(F.data == 'add_another_tool')
async def add_another_tool(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_name)
    await callback.message.edit_text(
        "Введите название нового инструмента:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool')
async def edit_tool_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tools = await tr.get_all()

        if not tools:
            await callback.answer("Нет доступных инструментов для редактирования")
            return
        
        await state.set_state(AdminTools.waiting_for_tool_edit)
        await callback.message.edit_text(
            "Выберите инструмент для редактирования:",
            reply_markup = await tools_edit_keyboard(tools)
        )
        await callback.answer()


@router.callback_query(F.data.startswith('edittool_'), AdminTools.waiting_for_tool_edit)
async def edit_tool_selected(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tool_id = int(callback.data.split('_')[1])
        tool = await tr.get_by_id(tool_id)
    
        if not tool:
            await callback.answer("Инструмент не найден")
            return
    
        cr = CategoryRepository(session_instance)
        category = await cr.get_by_id(tool.category_id)
        mr = ManufacturerRepository(session_instance)
        manufacturer = await mr.get_by_id(tool.manufacturer_id)
        
        # Получаем материалы инструмента
        tmr= ToolMaterialRepository(session_instance)
        material_ids = await tmr.get_material_ids_by_tool(tool_id)
        materials = await MaterialRepository(session_instance).get_by_ids(material_ids)
        materials_text = "\\".join([m.name for m in materials]) if materials else "Отсутствуют"
    
        await state.update_data(tool_id=tool_id)
        await callback.message.edit_text(
            f"Текущие данные инструмента:\n\n"
            f"Название: {tool.name}\n"
            f"Модель: {tool.model or 'Отсутствует'}\n"
            f"Описание: {tool.description or 'Отсутствует'}\n"
            f"Категория: {category.name}\n"
            f"Производитель: {manufacturer.name}\n"
            f"Материалы: {materials_text}\n"
            f"Вес (в кг): {tool.weight or 'Отсутствует'}\n"
            f"Цена (в ₽): {tool.price or 'Отсутствует'}\n"
            f"Изображения: {tool.image_url or 'Отсутствуют'}\n\n"
            "Что вы хотите изменить?",
            reply_markup=edit_tool_options_keyboard
        )
        await callback.answer()


@router.callback_query(F.data == 'edit_tool_name')
async def edit_tool_name_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='name')
    await callback.message.edit_text(
        "Введите новое название инструмента:",
        reply_markup = cancel_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_model')
async def edit_tool_model_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='model')
    await callback.message.edit_text(
        "Введите новую модель инструмента (или 'удалить' для очистки):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_description')
async def edit_tool_description_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='description')
    await callback.message.edit_text(
        "Введите новое описание инструмента (или 'удалить' для очистки):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_category')
async def edit_tool_category_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        await state.set_state(AdminTools.waiting_for_tool_edit_field)
        await state.update_data(edit_field='category_id')
        
        cr = CategoryRepository(session_instance)
        categories = await cr.get_all()
        if not categories:
            await callback.answer("Нет доступных категорий")
            return
        
        await callback.message.edit_text(
            "Выберите новую категорию:",
            reply_markup = await categories_select_keyboard(categories)
        )
        await callback.answer()


@router.callback_query(F.data == 'edit_tool_manufacturer')
async def edit_tool_manufacturer_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        await state.set_state(AdminTools.waiting_for_tool_edit_field)
        await state.update_data(edit_field='manufacturer_id')
        
        mr = ManufacturerRepository(session_instance)
        manufacturers = await mr.get_all()
        if not manufacturers:
            await callback.answer("Нет доступных производителей")
            return
        
        await callback.message.edit_text(
            "Выберите нового производителя:",
            reply_markup = await manufacturers_select_keyboard(manufacturers)
        )
        await callback.answer()


@router.callback_query(F.data == 'edit_tool_materials')
async def edit_tool_materials_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        tool_id = data['tool_id']
        
        mr = MaterialRepository(session_instance)
        materials = await mr.get_all()
        
        if not materials:
            await callback.answer("Нет доступных материалов")
            return
        
        tmr= ToolMaterialRepository(session_instance)
        current_material_ids = await tmr.get_material_ids_by_tool(tool_id)
        
        await state.set_state(AdminTools.waiting_for_tool_materials_edit)
        await callback.message.edit_text(
            "Выберите материалы инструмента:",
            reply_markup=await materials_select_keyboard(materials, current_material_ids, multi_select=True)
        )
        await callback.answer()


@router.callback_query(F.data == 'confirm_materials_edit', AdminTools.waiting_for_tool_materials_edit)
async def confirm_edit_tool_materials(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        tool_id = data['tool_id']
        selected_materials = data.get('materials', [])
        
        if not selected_materials:
            await callback.answer("Пожалуйста, выберите хотя бы один материал", show_alert=True)
            return
        
        # Обновляем связи
        tmr= ToolMaterialRepository(session_instance)
        await tmr.delete_by_tool(tool_id)
        for material_id in selected_materials:
            await tmr.create(tool_id, material_id)
        
        # Возвращаем к редактированию инструмента
        await state.set_state(AdminTools.waiting_for_tool_edit)
        tr = ToolRepository(session_instance)
        tool = await tr.get_by_id(tool_id)
        
        materials = []
        for material_id in selected_materials:
            material = await MaterialRepository(session_instance).get_by_id(material_id)
            if material:
                materials.append(material)
        
        materials_text = "\\".join([m.name for m in materials]) if materials else "Отсутствуют"
        
        await callback.message.edit_text(
            f"Материалы инструмента обновлены!\n\n"
            f"Текущие данные:\n"
            f"Название: {tool.name}\n"
            f"Материалы: {materials_text}\n\n"
            "Что вы хотите изменить?",
            reply_markup=edit_tool_options_keyboard
        )
    
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_weight')
async def edit_tool_weight_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='weight')
    await callback.message.edit_text(
        "Введите новый вес инструмента в кг (или 'удалить' для очистки):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_price')
async def edit_tool_price_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='price')
    await callback.message.edit_text(
        "Введите новый диапазон цен (или 'удалить' для очистки):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'edit_tool_images')
async def edit_tool_images_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminTools.waiting_for_tool_edit_field)
    await state.update_data(edit_field='image_url')
    await callback.message.edit_text(
        "Введите новые URL изображений через запятую (или 'удалить' для очистки):",
        reply_markup = skip_keyboard
    )
    await callback.answer()


@router.message(AdminTools.waiting_for_tool_edit_field)
async def edit_tool_field_process(message: Message, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        field = data['edit_field']
        tool_id = data['tool_id']
        value = None if message.text.lower() == 'удалить' else message.text
        
        if field == 'weight' and value is not None:
            try:
                value = float(value.replace(',', '.'))
                if value <= 0:
                    raise ValueError
            except ValueError:
                await message.answer("Пожалуйста, введите корректное число для веса (например: 1.5)")
                return
        
        try:
            tr = ToolRepository(session_instance)
            update_data = {field: value}
            await tr.update(tool_id, **update_data)
        
            tool = await tr.get_by_id(tool_id)
            cr = CategoryRepository(session_instance)
            category = await cr.get_by_id(tool.category_id)
            mr = ManufacturerRepository(session_instance)
            manufacturer = await mr.get_by_id(tool.manufacturer_id)
            tmr= ToolMaterialRepository(session_instance)
            materials = await MaterialRepository(session_instance).get_by_ids(
                await tmr.get_material_ids_by_tool(tool_id))
            
            materials_text = "\\".join([m.name for m in materials]) if materials else "Отсутствуют"
            
            await message.answer(
                f"Данные инструмента успешно обновлены!\n\n"
                f"Текущие данные:\n"
                f"Название: {tool.name}\n"
                f"Модель: {tool.model or 'Отсутствует'}\n"
                f"Описание: {tool.description or 'Отсутствует'}\n"
                f"Категория: {category.name}\n"
                f"Производитель: {manufacturer.name}\n"
                f"Материалы: {materials_text}\n"
                f"Вес (в кг): {tool.weight or 'Отсутствует'}\n"
                f"Цена (в ₽): {tool.price or 'Отсутствует'}\n"
                f"Изображения: {tool.image_url or 'Отсутствуют'}",
                reply_markup=edit_tool_options_keyboard
            )
        except Exception as e:
            await message.answer(
                f"Ошибка при обновлении инструмента: {str(e)}",
                reply_markup=back_to_tools_keyboard
            )
        
        await state.set_state(AdminTools.waiting_for_tool_edit)


@router.callback_query(F.data.startswith('selectcat_'), AdminTools.waiting_for_tool_edit_field)
async def edit_tool_category_select(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        if data.get('edit_field') != 'category_id':
            await callback.answer("Неверное состояние")
            return
        
        category_id = int(callback.data.split('_')[1])
        tool_id = data['tool_id']
        
        try:
            tr = ToolRepository(session_instance)
            await tr.update(tool_id, category_id=category_id)
            
            # Получаем обновленные данные инструмента
            tool = await tr.get_by_id(tool_id)
            cr = CategoryRepository(session_instance)
            category = await cr.get_by_id(tool.category_id)
            mr = ManufacturerRepository(session_instance)
            manufacturer = await mr.get_by_id(tool.manufacturer_id)
            
            tmr = ToolMaterialRepository(session_instance)
            material_ids = await tmr.get_material_ids_by_tool(tool_id)
            materials = await MaterialRepository(session_instance).get_by_ids(material_ids)
            materials_text = "\\".join([m.name for m in materials]) if materials else "Отсутствуют"
            
            await callback.message.edit_text(
                f"Категория инструмента успешно обновлена!\n\n"
                f"Текущие данные:\n"
                f"Название: {tool.name}\n"
                f"Описание: {tool.description or 'Отсутствует'}\n"
                f"Категория: {category.name}\n"
                f"Производитель: {manufacturer.name}\n"
                f"Материалы: {materials_text}\n"
                f"Вес (в кг): {tool.weight or 'Отсутствует'} кг\n"
                f"Цена (в ₽): {tool.price or 'Отсутствует'}\n"
                f"Изображения: {tool.image_url or 'Отсутствуют'}",
                reply_markup=edit_tool_options_keyboard
            )
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при обновлении категории: {str(e)}",
                reply_markup=back_to_tools_keyboard
            )
        
        await state.set_state(AdminTools.waiting_for_tool_edit)
        await callback.answer()


@router.callback_query(F.data.startswith('selectmanuf_'), AdminTools.waiting_for_tool_edit_field)
async def edit_tool_manufacturer_select(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        if data.get('edit_field') != 'manufacturer_id':
            await callback.answer("Неверное состояние")
            return
        
        manufacturer_id = int(callback.data.split('_')[1])
        tool_id = data['tool_id']
        
        try:
            tr = ToolRepository(session_instance)
            await tr.update(tool_id, manufacturer_id=manufacturer_id)
            
            # Получаем обновленные данные инструмента
            tool = await tr.get_by_id(tool_id)
            cr = CategoryRepository(session_instance)
            category = await cr.get_by_id(tool.category_id)
            mr = ManufacturerRepository(session_instance)
            manufacturer = await mr.get_by_id(tool.manufacturer_id)
            
            # Получаем материалы инструмента
            tmr= ToolMaterialRepository(session_instance)
            material_ids = await tmr.get_material_ids_by_tool(tool_id)
            materials = await MaterialRepository(session_instance).get_by_ids(material_ids)
            materials_text = "\\".join([m.name for m in materials]) if materials else "Отсутствуют"
            
            await callback.message.edit_text(
                f"Производитель инструмента успешно обновлен!\n\n"
                f"Текущие данные:\n"
                f"Название: {tool.name}\n"
                f"Описание: {tool.description or 'Отсутствует'}\n"
                f"Категория: {category.name}\n"
                f"Производитель: {manufacturer.name}\n"
                f"Материалы: {materials_text}\n"
                f"Вес (в кг): {tool.weight or 'Отсутствует'}\n"
                f"Цена (в ₽): {tool.price or 'Отсутствует'}\n"
                f"Изображения: {tool.image_url or 'Отсутствуют'}",
                reply_markup=edit_tool_options_keyboard
            )
        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при обновлении производителя: {str(e)}",
                reply_markup=back_to_tools_keyboard
            )
        
        await state.set_state(AdminTools.waiting_for_tool_edit)
        await callback.answer()


@router.callback_query(F.data == 'delete_tool')
async def delete_tool_start(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tools = await tr.get_all()

        if not tools:
            await callback.answer("Нет доступных инструментов для удаления")
            return
        
        await state.set_state(AdminTools.waiting_for_tool_delete)
        await callback.message.edit_text(
            "Выберите инструмент для удаления:",
            reply_markup = await tools_delete_keyboard(tools)
        )
        await callback.answer()


@router.callback_query(F.data.startswith('deletetool_'), AdminTools.waiting_for_tool_delete)
async def delete_tool_confirm(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        tr = ToolRepository(session_instance)
        tool_id = int(callback.data.split('_')[1])
        tool = await tr.get_by_id(tool_id)
    
        if not tool:
            await callback.answer("Инструмент не найден")
            return
    
        await state.update_data(tool_id=tool_id)
    
        reviews_count = await tr.get_reviews_count(tool_id)
        favorites_count = await tr.get_favorites_count(tool_id)
    
        warning_text = ""
        if reviews_count > 0:
            warning_text += f"⚠️ У инструмента есть {reviews_count} отзывов, которые будут удалены.\n"
        if favorites_count > 0:
            warning_text += f"⚠️ Инструмент находится в избранном у {favorites_count} пользователей.\n"
    
        if warning_text:
            await callback.message.edit_text(
                f"{warning_text}\n"
                f"Вы уверены, что хотите удалить инструмент '{tool.name}'?",
                reply_markup = confirm_delete_keyboard
            )
        else:
            await callback.message.edit_text(
                f"Вы уверены, что хотите удалить инструмент '{tool.name}'?",
                reply_markup = confirm_delete_keyboard
            )
    
        await callback.answer()


@router.callback_query(F.data == 'confirm_delete', AdminTools.waiting_for_tool_delete)
async def delete_tool_final(callback: CallbackQuery, state: FSMContext):
    async with session() as session_instance:
        data = await state.get_data()
        tool_id = data.get('tool_id')
        
        if not tool_id:
            await callback.answer("Ошибка: инструмент не выбран")
            return
        
        try:
            tr = ToolRepository(session_instance)
            tool = await tr.get_by_id(tool_id)

            if tool:
                await tr.delete(tool_id)
                await callback.message.edit_text(f"Инструмент '{tool.name}' успешно удален!")
            else:
                await callback.answer("Инструмент не найден")

        except Exception as e:
            await callback.message.edit_text(
                f"Ошибка при удалении инструмента: {str(e)}",
                reply_markup = back_to_tools_keyboard
            )
        
        await state.clear()


@router.callback_query(F.data == 'cancel_delete', AdminTools.waiting_for_tool_delete)
async def cancel_delete_tool(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Удаление отменено.",
        reply_markup = manage_tools_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_tools')
async def back_to_tools(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Управление инструментами:",
        reply_markup = manage_tools_keyboard
    )
    await callback.answer()


@router.callback_query(F.data == 'back_to_category')
async def back_to_category(callback: CallbackQuery):
    async with session() as session_instance:
        await callback.message.edit_text(
            'Выберите категорию инструментов:',
            reply_markup = await select_categories(session_instance)
        )
        await callback.answer()


@router.callback_query(F.data == 'back_to_tools_in_category')
async def back_to_category(callback: CallbackQuery):
    async with session() as session_instance:
        if not tm.tool_id:
            await callback.answer("Не удалось определить инструмент")
            return
    
        tr = ToolRepository(session_instance)
        tool = await tr.get_by_id(tm.tool_id)
        await callback.message.edit_text('Выберите инструмент из категории:', 
                                    reply_markup = await select_tools(int(tool.category_id), session_instance))
        await callback.answer()