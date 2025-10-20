from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from sqlalchemy import select

from config import ADMIN_ID
from database import get_session
from models import AnonymousMessage, AdminReply

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён!")
        return
    
    await message.answer(
        "👑 Панель администратора\n\n"
        "Здесь вы получаете анонимные сообщения от пользователей.\n\n"
        "Чтобы ответить пользователю:\n"
        "• Просто ответьте (reply) на полученное анонимное сообщение\n"
        "• После отправки вы получите отформатированное сообщение для публикации в канал",
        reply_markup=None
    )

@router.message(F.reply_to_message)
async def handle_admin_reply(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return

    replied_message_id = message.reply_to_message.message_id

    async for session in get_session():
        original_message = await session.execute(
            select(AnonymousMessage).where(AnonymousMessage.admin_thread_id == replied_message_id)
        )
        original_message = original_message.scalars().first()

        if not original_message:
            await message.reply("Не могу найти сообщение, на которое вы отвечаете.")
            return

        # Проверяем, является ли это медиа-сообщением (предложкой)
        if original_message.media_type:
            await message.reply(
                "ℹ️ Это анонимная предложка (фото/видео).\n"
                "Ответы на предложки не поддерживаются."
            )
            return

        # Создаем ответ администратора
        reply = AdminReply(
            message_id=original_message.id,
            reply_text=message.text
        )
        session.add(reply)
        await session.commit()

        # Отправляем ответ пользователю
        await bot.send_message(
            original_message.user_id,
            f"📩 Ответ от админа на ваше анонимное сообщение:\n\n{message.text}"
        )

        await message.reply("✅ Ответ отправлен пользователю!")

        # Форматируем сообщение для публикации в канал
        formatted_text = (
            f"❓ <b>Анонимный вопрос:</b>\n\n"
            f"<blockquote>{original_message.message_text}</blockquote>\n\n"
            f"💬 <b>Ответ:</b>\n\n"
            f"{message.text}"
        )

        await message.answer(
            formatted_text,
            parse_mode=ParseMode.HTML
        )
