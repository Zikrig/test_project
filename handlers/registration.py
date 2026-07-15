import asyncio
import logging
import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.common import edit_or_send_text, notify_admin
from keyboards import back_kb, main_menu_kb, source_kb
from services.db import save_registration
from services.sheets import append_registration
from states import Registration

logger = logging.getLogger(__name__)
router = Router()

SOURCE_LABELS = {
    "source_friends": "От друзей",
    "source_internet": "Через интернет",
}

# Only digits and optional leading '+'; allowed.
PHONE_RE = re.compile(r"^\+?\d+$")


def _is_valid_phone(value: str) -> bool:
    return bool(PHONE_RE.fullmatch(value))


@router.callback_query(F.data == "register")
async def start_registration(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.name)
    await edit_or_send_text(
        callback,
        "Регистрация\n\nКак вас зовут?",
        reply_markup=back_kb("back_main"),
    )
    await callback.answer()


@router.message(Registration.name, F.text)
async def process_name(message: Message, state: FSMContext) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer(
            "Пожалуйста, введите имя текстом.",
            reply_markup=back_kb("back_main"),
        )
        return
    await state.update_data(name=name)
    await state.set_state(Registration.age)
    await message.answer(
        "Сколько вам лет?",
        reply_markup=back_kb("back_to_name"),
    )


@router.callback_query(Registration.age, F.data == "back_to_name")
async def back_to_name(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.name)
    await edit_or_send_text(
        callback,
        "Регистрация\n\nКак вас зовут?",
        reply_markup=back_kb("back_main"),
    )
    await callback.answer()


@router.message(Registration.age, F.text)
async def process_age(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text.isdigit() or not (1 <= int(text) <= 120):
        await message.answer(
            "Введите возраст числом от 1 до 120.",
            reply_markup=back_kb("back_to_name"),
        )
        return
    await state.update_data(age=int(text))
    await state.set_state(Registration.phone)
    await message.answer(
        "Укажите номер телефона.\nМожно использовать только цифры и знак +.",
        reply_markup=back_kb("back_to_age"),
    )


@router.callback_query(Registration.phone, F.data == "back_to_age")
async def back_to_age_from_phone(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.age)
    await edit_or_send_text(
        callback,
        "Сколько вам лет?",
        reply_markup=back_kb("back_to_name"),
    )
    await callback.answer()


@router.message(Registration.phone, F.text)
async def process_phone(message: Message, state: FSMContext) -> None:
    phone = (message.text or "").strip()
    if not _is_valid_phone(phone):
        await message.answer(
            "Номер телефона может содержать только цифры и знак + "
            "(например, +79991234567).",
            reply_markup=back_kb("back_to_age"),
        )
        return
    await state.update_data(phone=phone)
    await state.set_state(Registration.source)
    await message.answer(
        "Как вы узнали о нас?",
        reply_markup=source_kb(),
    )


@router.callback_query(Registration.source, F.data == "back_to_phone")
@router.callback_query(Registration.source_other, F.data == "back_to_phone")
async def back_to_phone(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.phone)
    await edit_or_send_text(
        callback,
        "Укажите номер телефона.\nМожно использовать только цифры и знак +.",
        reply_markup=back_kb("back_to_age"),
    )
    await callback.answer()


@router.callback_query(
    Registration.source,
    F.data.in_({"source_friends", "source_internet"}),
)
async def process_source_choice(callback: CallbackQuery, state: FSMContext) -> None:
    source = SOURCE_LABELS[callback.data]
    await _finish_registration(callback, state, source)


@router.callback_query(Registration.source, F.data == "source_other")
async def process_source_other(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.source_other)
    await edit_or_send_text(
        callback,
        "Напишите, откуда вы о нас узнали.",
        reply_markup=back_kb("back_to_source"),
    )
    await callback.answer()


@router.callback_query(Registration.source_other, F.data == "back_to_source")
async def back_to_source(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Registration.source)
    await edit_or_send_text(
        callback,
        "Как вы узнали о нас?",
        reply_markup=source_kb(),
    )
    await callback.answer()


@router.message(Registration.source_other, F.text)
async def process_source_other_text(message: Message, state: FSMContext) -> None:
    source = (message.text or "").strip()
    if not source:
        await message.answer(
            "Пожалуйста, опишите текстом, откуда узнали о нас.",
            reply_markup=back_kb("back_to_source"),
        )
        return
    await _finish_registration_message(message, state, source)


async def _finish_registration(
    callback: CallbackQuery,
    state: FSMContext,
    source: str,
) -> None:
    message = callback.message
    if message is None or callback.from_user is None:
        await callback.answer()
        return
    data = await state.get_data()
    await state.clear()
    await _persist_and_notify(
        bot=callback.bot,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        name=data["name"],
        age=data["age"],
        phone=data["phone"],
        source=source,
    )
    await edit_or_send_text(
        callback,
        "Спасибо! Регистрация завершена. Мы свяжемся с вами.",
        reply_markup=main_menu_kb(),
    )
    await callback.answer()


async def _finish_registration_message(
    message: Message,
    state: FSMContext,
    source: str,
) -> None:
    if message.from_user is None:
        return
    data = await state.get_data()
    await state.clear()
    await _persist_and_notify(
        bot=message.bot,
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        name=data["name"],
        age=data["age"],
        phone=data["phone"],
        source=source,
    )
    await message.answer(
        "Спасибо! Регистрация завершена. Мы свяжемся с вами.",
        reply_markup=main_menu_kb(),
    )


async def _persist_and_notify(
    *,
    bot,
    telegram_id: int,
    username: str | None,
    name: str,
    age: int,
    phone: str,
    source: str,
) -> None:
    await save_registration(telegram_id, username, name, age, phone, source)
    try:
        await asyncio.to_thread(
            append_registration,
            telegram_id,
            username,
            name,
            age,
            phone,
            source,
        )
    except Exception:
        logger.exception("Failed to append registration to Google Sheets")
    try:
        await notify_admin(
            bot,
            telegram_id=telegram_id,
            username=username,
            name=name,
            age=age,
            phone=phone,
            source=source,
        )
    except Exception:
        logger.exception("Failed to notify admin")
