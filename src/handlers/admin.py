from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
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
        "Здесь вы получаете анонимные сообщения от пользователей.\n"
        "Чтобы ответить - просто ответьте (reply) на полученное сообщение.",
        reply_markup=None
    )

@router.message(F.reply_to_message)
async def handle_admin_reply(message: Message, bot):
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

        # Создаем ответ администратора
        reply = AdminReply(
            message_id=original_message.id,
            reply_text=message.text
        )
        session.add(reply)
        await session.commit()

        await bot.send_message(
            original_message.user_id,
            f"📩 Ответ от админа на ваше анонимное сообщение:\n\n{message.text}"
        )

    await message.reply("✅ Ответ отправлен пользователю!")
