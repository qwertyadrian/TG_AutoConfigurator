import os
from random import choice

from loguru import logger
from pyrogram import Filters, Message

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import messages

# Символы, на которых можно разбить сообщение
message_breakers = [":", " ", "\n"]
max_message_length = 4091


def admin_check(bot: AutoConfigurator, message: Message):
    logger.info(
        "Пользователь {message.from_user.first_name} {message.from_user.last_name} "
        "c ID {message.from_user.id} использовал команду {message.text}",
        message=message,
    )
    return message.from_user.id == bot.admin_id


@AutoConfigurator.on_message(Filters.command(commands=["start", "help"]) & Filters.private)
def send_welcome(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        message.reply(messages.HELP.format(bot.get_me().username), parse_mode="html")


@AutoConfigurator.on_message(Filters.command(commands="get_full_logs") & Filters.private)
def send_full_logs(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        try:
            logs = sorted(os.listdir(bot.bot_logs_folder_path))
            for i in range(len(logs)):
                logs[i] = os.path.join(bot.bot_logs_folder_path, logs[i])
        except (FileNotFoundError, IndexError):
            logs = None
        if logs:
            a = message.reply("Отправка логов...")
            try:
                a.reply_document(logs[-1])
            except ValueError:
                a.edit("Последний лог файл пустой")
        else:
            message.reply("Логи не найдены.")


@AutoConfigurator.on_message(Filters.command(commands="get_last_logs") & Filters.private)
def send_last_logs(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        try:
            logs = os.path.join(bot.bot_logs_folder_path, sorted(os.listdir(bot.bot_logs_folder_path))[-1])
        except (FileNotFoundError, IndexError):
            logs = None
        try:
            lines = int(message.command[1])
        except (ValueError, IndexError):
            lines = 15
        if logs:
            with open(logs, "r", encoding="utf-8") as f:
                last_logs = "".join(f.readlines()[-lines:])
                last_logs = "Последние {} строк логов:\n\n".format(str(lines)) + last_logs
            for msg in split(last_logs):
                message.reply(msg)
        else:
            message.reply("Логи не найдены.")


@AutoConfigurator.on_message(Filters.command(commands=["list", "sources_list"]) & Filters.private)
def source_list(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        bot.reload_config()
        sources_list = bot.config.sections()[3:] if bot.config.has_section("proxy") else bot.config.sections()[2:]
        sources = "Список источников:\nИсточник        ---->        Назначение  (ID последнего отправленного поста)\n\n"
        for source in sources_list:
            sources += "https://vk.com/{}        ---->        {}  ({})\n".format(
                source, bot.config.get(source, "channel"), bot.config.get(source, "last_id")
            )
        sources += "\nДля удаления источника отправьте команду /remove <домен группы вк>\nНапример, /remove " + choice(
            sources_list
        )
        message.reply(sources, disable_web_page_preview=True, parse_mode=None)


@AutoConfigurator.on_message(
    Filters.command(commands=["remove_source", "remove", "delete", "delete_source"]) & Filters.private
)
def remove_source(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        if len(message.command) > 1:
            bot.reload_config()
            section = bot.remove_config_section(message.command[1])
            info = (
                "Источник {0[0]} был удален.\nДля его восстановления используйте команду"
                " `/add {0[0]} {0[1]} {0[2]}`".format(section)
            )
            message.reply(info)
        else:
            message.reply(messages.REMOVE)


@AutoConfigurator.on_message(Filters.command(commands=["add"]) & Filters.private)
def add_source(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        if len(message.command) >= 3:
            bot.reload_config()
            section = bot.add_config_section(*message.command[1:])
            info = "Источник {0[0]} был добавлен.".format(section)
            message.reply(info)
        else:
            message.reply(messages.ADD)


@AutoConfigurator.on_message(Filters.command(commands=["get_config"]) & Filters.private)
def get_config(bot: AutoConfigurator, message: Message):
    if admin_check(bot, message):
        message.reply("Конфигурация бота:\n ```{}```".format(open(bot.config_path).read()))
        message.reply_document(document=bot.config_path, caption="Файл конфигурации бота.")


def split(text):
    if len(text) >= max_message_length:
        last_index = max(map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
        good_part = text[:last_index]
        bad_part = text[last_index + 1:]
        return [good_part] + split(bad_part)
    else:
        return [text]
