from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Регистрация", callback_data="register")],
            [InlineKeyboardButton(text="О нас", callback_data="about_us")],
            [InlineKeyboardButton(text="О боте", callback_data="about_bot")],
        ]
    )


def back_kb(callback_data: str = "back_main") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=callback_data)]
        ]
    )


def source_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="От друзей", callback_data="source_friends"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Через интернет", callback_data="source_internet"
                )
            ],
            [InlineKeyboardButton(text="Другое", callback_data="source_other")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_phone")],
        ]
    )
