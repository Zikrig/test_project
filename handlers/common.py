from pathlib import Path

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from config import settings
from keyboards import main_menu_kb

WELCOME_TEXT = (
    "Добро пожаловать на вечеринку!\n\n"
    "Адрес: улица Пушкина, дом Колотушкина.\n\n"
    "Выберите действие:"
)

ABOUT_US_TEXT = (
    "О нас\n\n"
    "Мы устраиваем камерные вечеринки в уютной атмосфере. "
    "Музыка, общение и хорошее настроение по адресу: "
    "улица Пушкина, дом Колотушкина."
)

ABOUT_BOT_TEXT = (
    "О боте\n\n"
    "Этот бот помогает записаться на вечеринку: "
    "оставьте имя, возраст и расскажите, откуда узнали о нас. "
    "После регистрации организаторы получат вашу заявку."
)


async def send_welcome(message: Message) -> None:
    image_path = Path(settings.welcome_image_path)
    if image_path.is_file():
        await message.answer_photo(
            photo=FSInputFile(image_path),
            caption=WELCOME_TEXT,
            reply_markup=main_menu_kb(),
        )
    else:
        await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


async def edit_or_send_text(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
) -> None:
    message = callback.message
    if message is None:
        return
    if message.photo:
        await message.delete()
        await message.answer(text, reply_markup=reply_markup)
    else:
        await message.edit_text(text, reply_markup=reply_markup)


async def back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    message = callback.message
    if message is None:
        return
    await message.delete()
    await send_welcome(message)


async def notify_admin(
    bot: Bot,
    *,
    telegram_id: int,
    username: str | None,
    name: str,
    age: int,
    phone: str,
    source: str,
) -> None:
    username_line = f"@{username}" if username else "—"
    text = (
        "Новая регистрация на вечеринку\n\n"
        f"Имя: {name}\n"
        f"Возраст: {age}\n"
        f"Телефон: {phone}\n"
        f"Откуда узнали: {source}\n"
        f"Telegram ID: {telegram_id}\n"
        f"Username: {username_line}"
    )
    await bot.send_message(settings.admin_telegram_id, text)
