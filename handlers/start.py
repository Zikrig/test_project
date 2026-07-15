from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from handlers.common import (
    ABOUT_BOT_TEXT,
    ABOUT_US_TEXT,
    back_to_main,
    edit_or_send_text,
    send_welcome,
)
from keyboards import back_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await send_welcome(message)


@router.callback_query(F.data == "about_us")
async def about_us(callback: CallbackQuery) -> None:
    await edit_or_send_text(callback, ABOUT_US_TEXT, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "about_bot")
async def about_bot(callback: CallbackQuery) -> None:
    await edit_or_send_text(callback, ABOUT_BOT_TEXT, reply_markup=back_kb())
    await callback.answer()


@router.callback_query(F.data == "back_main")
async def on_back_main(callback: CallbackQuery, state: FSMContext) -> None:
    await back_to_main(callback, state)
    await callback.answer()
