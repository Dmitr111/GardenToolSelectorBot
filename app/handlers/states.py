from aiogram.fsm.state import StatesGroup, State

class Reviews(StatesGroup):
    waiting_for_text = State()
    waiting_for_rating = State()

class Search(StatesGroup):
    waiting_for_query = State()

class AdminUser(StatesGroup):
    waiting_for_user_telegram_id = State()

class AdminCategories(StatesGroup):
    waiting_for_category_name = State()
    waiting_for_category_description = State()
    waiting_for_category_edit = State()
    waiting_for_category_edit_name = State()
    waiting_for_category_edit_description = State()
    waiting_for_category_delete = State()

class AdminManufacturers(StatesGroup):
    waiting_for_manufacturer_name = State()
    waiting_for_manufacturer_country = State()
    waiting_for_manufacturer_website = State()
    waiting_for_manufacturer_edit = State()
    waiting_for_manufacturer_edit_name = State()
    waiting_for_manufacturer_edit_country = State()
    waiting_for_manufacturer_edit_website = State()
    waiting_for_manufacturer_delete = State()

class AdminTools(StatesGroup):
    waiting_for_tool_name = State()
    waiting_for_tool_model = State() 
    waiting_for_tool_description = State()
    waiting_for_tool_category = State()
    waiting_for_tool_manufacturer = State()
    waiting_for_tool_materials_select = State()
    waiting_for_tool_weight = State()
    waiting_for_tool_price = State()
    waiting_for_tool_images = State()
    waiting_for_tool_edit = State()
    waiting_for_tool_materials_edit = State()
    waiting_for_tool_edit_field = State()
    waiting_for_tool_delete = State()

class CompareTools(StatesGroup):
    waiting_for_first_tool = State()
    waiting_for_second_tool = State()

class FilterTools(StatesGroup):
    waiting_for_category = State()
    waiting_for_manufacturer = State()
    waiting_for_min_price = State()
    waiting_for_max_price = State()
    waiting_for_min_rating = State()
    waiting_for_max_rating = State()
    applying_filters = State()

class AdminRecommendations(StatesGroup):
    waiting_for_recommendation_proficiency_level = State()
    waiting_for_recommendation_category = State()
    waiting_for_recommendation_text = State()
    waiting_for_recommendation_edit = State()
    waiting_for_recommendation_edit_proficiency_level = State()
    waiting_for_recommendation_edit_category = State()
    waiting_for_recommendation_edit_text = State()
    waiting_for_recommendation_delete = State()

class UpdateProficiency(StatesGroup):
    waiting_for_level = State()