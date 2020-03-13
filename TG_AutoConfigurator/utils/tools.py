from typing import List, Union

from loguru import logger
from pyrogram import CallbackQuery, InlineKeyboardButton, InlineQuery, Message

from ..TG_AutoConfigurator import AutoConfigurator

# Символы, на которых можно разбить сообщение
message_breakers = [":", " ", "\n"]
max_message_length = 4091


def admin_check(bot: AutoConfigurator, message: Union[Message, InlineQuery, CallbackQuery]) -> bool:
    if isinstance(message, Message):
        logger.info(
            "Пользователь {message.from_user.first_name} {message.from_user.last_name} "
            "c ID {message.from_user.id} использовал команду {message.text}",
            message=message,
        )
    elif isinstance(message, InlineQuery):
        logger.info(
            "Пользователь {message.from_user.first_name} {message.from_user.last_name} "
            "c ID {message.from_user.id} выполнил запрос со следующим текстом: {message.query}",
            message=message,
        )
    elif isinstance(message, CallbackQuery):
        logger.info(
            "Пользователь {message.from_user.first_name} {message.from_user.last_name} "
            "c ID {message.from_user.id} использовал обратный запрос со следущим содержимым {message.data}",
            message=message,
        )
    return message.from_user.id == bot.admin_id


def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int = 1,
    header_buttons: List[InlineKeyboardButton] = None,
    footer_buttons: List[InlineKeyboardButton] = None,
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i: i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def split(text: str):
    if len(text) >= max_message_length:
        last_index = max(map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
        good_part = text[:last_index]
        bad_part = text[last_index + 1:]
        return [good_part] + split(bad_part)
    else:
        return [text]
