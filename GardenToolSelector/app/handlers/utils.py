from aiogram.types import Message
from typing import Optional
from ..database.db import async_session as session
from ..database.repositories import CategoryRepository
from ..keyboards.selection_keyboards import *

class ToolMessage:
    def __init__(self):
        self.message_id: Optional[int] = None
        self.chat_id: Optional[int] = None
        self.tool_id: Optional[int] = None
    
    async def delete(self, bot):
        if self.message_id and self.chat_id:
            try:
                await bot.delete_message(self.chat_id, self.message_id)
            except Exception:
                pass
        self.clear()
    
    def update(self, message: Message, tool_id: int = None):
        self.message_id = message.message_id
        self.chat_id = message.chat.id
        if tool_id is not None:
            self.tool_id = tool_id
    
    def clear(self):
        self.message_id = None
        self.chat_id = None
        self.tool_id = None

class ReviewMessages:
    def __init__(self):
        self.messages = []
    
    async def delete_all(self, bot):
        for msg in self.messages:
            try:
                await bot.delete_message(msg['chat_id'], msg['message_id'])
            except Exception:
                pass
        self.clear()
    
    def add(self, message: Message):
        self.messages.append({
            'message_id': message.message_id,
            'chat_id': message.chat.id
        })
    
    def clear(self):
        self.messages = []

tool_message = ToolMessage()
review_messages = ReviewMessages()
current_filters = {}

async def show_tools_selection(message: Message):
    async with session() as session_instance:
        cr = CategoryRepository(session_instance)
        await message.delete()
        await tool_message.delete(message.bot)
        categories = await cr.get_all()

        if not categories:
            await message.answer('Категории пока отсутсвуют.')
        else:
            sent_message = await message.answer('Выберите категорию инструментов:', 
                                            reply_markup=await select_categories(session_instance))
            tool_message.update(sent_message)