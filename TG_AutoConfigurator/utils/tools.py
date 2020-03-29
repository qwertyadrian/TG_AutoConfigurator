from typing import List, Union, Tuple

from loguru import logger
from pyrogram import CallbackQuery, InlineKeyboardButton, InlineQuery, Message, InlineKeyboardMarkup

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import messages

# Символы, на которых можно разбить сообщение
message_breakers = [":", " ", "\n"]
max_message_length = 4091


def admin_check(bot: AutoConfigurator, message: Union[Message, InlineQuery, CallbackQuery]) -> bool:
    if isinstance(message, Message):
        logger.info(
            messages.LOG_MESSAGE,
            message=message,
        )
    elif isinstance(message, InlineQuery):
        logger.info(
            messages.LOG_INLINE_QUERY,
            message=message,
        )
    elif isinstance(message, CallbackQuery):
        logger.info(
            messages.LOG_CALLBACK_QUERY,
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


def generate_setting_info(bot: AutoConfigurator, source: str) -> Tuple[str, InlineKeyboardMarkup]:
    if source != "global":
        text = messages.INLINE_INPUT_MESSAGE_CONTENT.format(
            source,
            bot.config.get(source, "channel"),
            bot.config.get(source, "last_id", fallback=0),
            bot.config.get(source, "last_story_id", fallback=0),
            bot.config.get(source, "pinned_id", fallback=0),
        ) + "Отправляемые вложения: `{}`".format(
            bot.config.get(source, "what_to_send", fallback=bot.config.get("global", "what_to_send", fallback="всё"))
        )
        footer_button = [InlineKeyboardButton("Удалить источник", callback_data="delete " + source)]
    else:
        text = messages.GLOBAL_SETTINGS.format(
            bot.config.get(source, "what_to_send", fallback=bot.config.get("global", "what_to_send", fallback="всё"))
        )
        footer_button = None
    reposts = bot.config.get(source, "send_reposts", fallback=bot.config.get("global", "send_reposts", fallback=0))
    if reposts in ("yes", "all", "True", 2):
        reposts = "✔️"
    elif reposts in ("no", "False", 0):
        reposts = "❌"
    elif reposts in ("post_only", 1):
        reposts = "Только пост"
        text += messages.PARTIAL_REPOSTS
    button_list = [
        InlineKeyboardButton(
            "Подписи: {}".format(
                "✔️"
                if bot.config.getboolean(
                    source, "sign_posts", fallback=bot.config.getboolean("global", "sign_posts", fallback=True)
                )
                else "❌"
            ),
            callback_data="switch {} sign_posts".format(source),
        ),
        InlineKeyboardButton("Репосты: {}".format(reposts), callback_data="show {} send_reposts".format(source)),
        InlineKeyboardButton(
            "Уведомления: {}".format(
                "❌"
                if bot.config.getboolean(
                    source,
                    "disable_notification",
                    fallback=bot.config.getboolean("global", "disable_notification", fallback=False),
                )
                else "✔️"
            ),
            callback_data="switch {} disable_notification".format(source),
        ),
        InlineKeyboardButton(
            "Истории: {}".format(
                "✔️"
                if bot.config.getboolean(
                    source, "send_stories", fallback=bot.config.getboolean("global", "send_stories", fallback=False)
                )
                else "❌"
            ),
            callback_data="switch {} send_stories".format(source),
        ),
        InlineKeyboardButton(
            "Превью ссылок: {}".format(
                "❌"
                if bot.config.getboolean(
                    source,
                    "disable_web_page_preview",
                    fallback=bot.config.getboolean("global", "disable_web_page_preview", fallback=True),
                )
                else "✔️"
            ),
            callback_data="switch {} disable_web_page_preview".format(source),
        ),
    ]

    return text, InlineKeyboardMarkup(build_menu(button_list, footer_buttons=footer_button, n_cols=2))
