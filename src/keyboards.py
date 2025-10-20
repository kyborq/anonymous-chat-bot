from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def get_user_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="✉️ Отправить сообщение")
    builder.button(text="📸 Отправить фото/видео")
    builder.button(text="ℹ️ Информация")
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_cancel_button() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)