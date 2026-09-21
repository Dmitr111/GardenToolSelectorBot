from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters.command import CommandStart, Command
from aiogram.fsm.context import FSMContext
from ..database.db import async_session as session
from ..database.repositories import UserRepository, ProficiencyLevelRepository
from .utils import show_tools_selection
from .states import Search, FilterTools, UpdateProficiency
from ..keyboards.common_keyboards import *
from ..keyboards.proficiency_keyboards import *
from ..keyboards.filters_keyboards import *

router = Router()

MESSAGE_HELP = '''
⭐ /start - Запустить бота и начать использование.
⭐ /select - Выбрать категорию инструментов.
⭐ /search - Найти садовый или огородный инструмент.
⭐ /filter - Отфильтровать результаты поиска по параметрам.
⭐ /about - Узнать больше о возможностях бота

Если у вас возникли вопросы, то @Luuckyyy всегда готов вам помочь. 
Также буду рад получить обратную связь.
'''

MESSAGE_START = '''
Привет! Вот, что я умею:

⭐ /start - Запустить бота и начать использование.
⭐ /help - Получить список всех доступных команд и помощь
⭐ /select - Выбрать категорию инструментов.
⭐ /search - Найти садовый или огородный инструмент.
⭐ /filter - Отфильтровать результаты поиска по параметрам.
⭐ /about - Узнать больше о возможностях бота

❗ При удалении этого сообщения кнопки выбора инструментов пропадут. Чтобы их вернуть, введите /start еще раз! 🙂
'''

MESSAGE_ABOUT = '''
🌱 Бот для подбора садовых и огородных инструментов! 
Поможет выбрать оптимальный инвентарь с учётом ваших потребностей. 
🔍 Функции: поиск по категориям (почва, растения, полив, урожай), 
сравнение характеристик, фильтрация по параметрам (материал, вес, цена), отзывы и рейтинги. 
🚀Поддержка рекомендаций по уровню опыта владения навыками садоводства и огородничества. 
Упрощайте выбор инструментов с помощью удобного и понятного интерфейса!
'''

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        pr = ProficiencyLevelRepository(session_instance)
        user = await ur.get_by_telegram_id(message.from_user.id)
        await message.delete()
        if not user:
            levels = await pr.get_all()
            description_text = ''
            for level in levels:
                description_text += f"- {level.name}: {level.description}\n"
            description_text += '\nВыберите ваш уровень владения навыками садоводства:'
            await message.answer(description_text, reply_markup=await get_proficiency_keyboard(session_instance))
            await state.set_state(UpdateProficiency.waiting_for_level)
            await ur.create(message.from_user.username, message.from_user.id)
        else:
            await message.answer(MESSAGE_START, reply_markup=start_keyboard)

@router.message(Command('profile'))
@router.message(F.text == '⚙️Профиль')
async def cmd_profile(message: Message):
    async with session() as session_instance:
        ur = UserRepository(session_instance)
        user = await ur.get_by_telegram_id(message.from_user.id)
        pr = ProficiencyLevelRepository(session_instance)
        proficiency = await pr.get_by_id(user.proficiency_level_id)
        await message.delete()
        text = f'Это ваш профиль{f", {user.username}" if user.username else ""}\nВаш уровень владения: {proficiency.name}'
        await message.answer(text, reply_markup=await profile_keyboard(user.telegram_id, session_instance))

@router.message(Command('help'))
@router.message(F.text == '❓Помощь')
async def cmd_help(message: Message):
    await message.delete()
    await message.answer(MESSAGE_HELP)

@router.message(Command('select'))
@router.message(F.text == '🔨Выбор инструментов')
async def cmd_selection(message: Message):
    await show_tools_selection(message)

@router.message(Command('search'))
@router.message(F.text == '🔍Поиск инструмента')
async def cmd_search(message: Message, state: FSMContext):
    await message.answer("Введите название инструмента или часть названия для поиска:", reply_markup=cancel_keyboard)
    await state.set_state(Search.waiting_for_query)
    await message.delete()

@router.message(Command("filter"))
@router.message(F.text == '✏️Фильтры')
async def filter_tools_command(message: Message, state: FSMContext):
    await message.delete()
    await message.answer("Выберите параметры фильтрации:", reply_markup=get_filters_keyboard())
    await state.set_state(FilterTools.applying_filters)

@router.message(Command("about"))
async def filter_tools_command(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(MESSAGE_ABOUT)

@router.message(F.text)
async def unknown_command_handler(message: Message):
    await message.reply("Извините, но бот не знает такой команды. Воспользуйтесь командой /help для справки")