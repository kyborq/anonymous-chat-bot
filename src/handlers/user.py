from aiogram import Router, F, Bot
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
    waiting_for_media = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в анонимный чат!\n\n"
        "Вы можете отправить сообщение или медиа (фото/видео) админу анонимно.\n"
        "Админ может ответить на ваше сообщение.\n\n"
        "Выберите действие:",
        reply_markup=get_user_menu()
    )

@router.message(F.text == "ℹ️ Информация")
async def cmd_info(message: Message):
    await message.answer(
        "🤖 Анонимный чат-бот\n\n"
        "Возможности:\n"
        "• Отправка текстовых сообщений анонимно\n"
        "• Отправка фото и видео (предложки)\n"
        "• Получение ответов от админа\n\n"
        "Ваши личные данные не будут раскрыты.",
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

@router.message(F.text == "📸 Отправить фото/видео")
async def cmd_send_media(message: Message, state: FSMContext):
    await message.answer(
        "📸 Отправьте фото или видео:\n\n"
        "Вы можете добавить подпись к медиа.\n"
        "Нажмите 'Отмена', чтобы прервать отправку.",
        reply_markup=get_cancel_button()
    )
    await state.set_state(AnonymousMessageState.waiting_for_media)

@router.message(F.text == "❌ Отмена")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Отправка отменена.",
        reply_markup=get_user_menu()
    )

@router.message(AnonymousMessageState.waiting_for_message)
async def process_anonymous_message(message: Message, state: FSMContext, bot: Bot):
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

@router.message(AnonymousMessageState.waiting_for_media, F.photo)
async def process_anonymous_photo(message: Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]  # Берем фото наибольшего размера
    caption = message.caption or ""
    
    async for session in get_session():
        new_message = AnonymousMessage(
            user_id=message.from_user.id,
            message_text=None,
            media_type="photo",
            media_file_id=photo.file_id,
            caption=caption
        )
        session.add(new_message)
        await session.commit()
        
        # Отправляем фото админу
        caption_for_admin = f"📸 Анонимная предложка (фото)"
        if caption:
            caption_for_admin += f"\n\nПодпись: {caption}"
        
        sent_to_admin = await bot.send_photo(
            ADMIN_ID,
            photo=photo.file_id,
            caption=caption_for_admin
        )
        
        new_message.admin_thread_id = sent_to_admin.message_id
        await session.commit()
    
    await message.answer(
        "✅ Ваше фото отправлено админу анонимно!",
        reply_markup=get_user_menu()
    )
    await state.clear()

@router.message(AnonymousMessageState.waiting_for_media, F.video)
async def process_anonymous_video(message: Message, state: FSMContext, bot: Bot):
    video = message.video
    caption = message.caption or ""
    
    async for session in get_session():
        new_message = AnonymousMessage(
            user_id=message.from_user.id,
            message_text=None,
            media_type="video",
            media_file_id=video.file_id,
            caption=caption
        )
        session.add(new_message)
        await session.commit()
        
        # Отправляем видео админу
        caption_for_admin = f"🎥 Анонимная предложка (видео)"
        if caption:
            caption_for_admin += f"\n\nПодпись: {caption}"
        
        sent_to_admin = await bot.send_video(
            ADMIN_ID,
            video=video.file_id,
            caption=caption_for_admin
        )
        
        new_message.admin_thread_id = sent_to_admin.message_id
        await session.commit()
    
    await message.answer(
        "✅ Ваше видео отправлено админу анонимно!",
        reply_markup=get_user_menu()
    )
    await state.clear()

@router.message(AnonymousMessageState.waiting_for_media)
async def process_wrong_media_type(message: Message, state: FSMContext):
    await message.answer(
        "⚠️ Пожалуйста, отправьте фото или видео.\n\n"
        "Или нажмите 'Отмена' для отмены.",
        reply_markup=get_cancel_button()
    )