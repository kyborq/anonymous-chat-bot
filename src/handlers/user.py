from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import ADMIN_ID
from database import get_session
from models import AnonymousMessage
from keyboards import get_user_menu, get_cancel_button

router = Router()

class AnonymousMessageState(StatesGroup):
    waiting_for_message = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в анонимный чат!\n\n"
        "Вы можете отправить сообщение админу анонимно. "
        "Админ может ответить на ваше сообщение.\n\n"
        "Нажмите кнопку ниже, чтобы отправить сообщение.",
        reply_markup=get_user_menu()
    )

@router.message(F.text == "ℹ️ Информация")
async def cmd_info(message: Message):
    await message.answer(
        "🤖 Анонимный чат-бот\n\n"
        "Отправляйте сообщения админу анонимно. "
        "Ваши личные данные не будут раскрыты.\n\n"
        "Админ может ответить на ваше сообщение, и ответ придёт вам в этот чат.",
        reply_markup=get_user_menu()
    )

@router.message(F.text == "✉️ Отправить сообщение")
async def cmd_send_message(message: Message, state: FSMContext):
    await message.answer(
        "✍️ Напишите ваше сообщение:\n\n"
        "Нажмите 'Отмена', чтобы прервать отправку.",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AnonymousMessageState.waiting_for_message)

@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отправка отменена.",
        reply_markup=get_user_menu()
    )

@router.message(AnonymousMessageState.waiting_for_message)
async def process_anonymous_message(message: Message, state: FSMContext, bot):
    async for session in get_session():
        new_message = AnonymousMessage(
            user_id=message.from_user.id,
            message_text=message.text
        )
        session.add(new_message)
        await session.commit()
        
        sent_to_admin = await bot.send_message(
            ADMIN_ID,
            f"📨 Новое анонимное сообщение:\n\n{message.text}\n\n"
            f"Ответьте на это сообщение, чтобы отправить ответ пользователю."
        )
        
        new_message.admin_thread_id = sent_to_admin.message_id
        await session.commit()
    
    await message.answer(
        "✅ Ваше сообщение отправлено админу анонимно!\n\n"
        "Если админ ответит на него, вы получите ответ здесь.",
        reply_markup=get_user_menu()
    )
    await state.clear()