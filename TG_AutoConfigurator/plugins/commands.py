import os
from random import choice

from pyrogram import Filters, Message, InlineKeyboardButton, InlineKeyboardMarkup

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import messages, tools


@AutoConfigurator.on_message(Filters.command(commands=["start", "help"]) & Filters.private)
def send_welcome(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
        button = [[InlineKeyboardButton("Поиск среди источников", switch_inline_query_current_chat="")]]
        message.reply(messages.HELP.format(bot.get_me().username), parse_mode="html", disable_web_page_preview=True,
                      reply_markup=InlineKeyboardMarkup(button))


@AutoConfigurator.on_message(Filters.command(commands="get_full_logs") & Filters.private)
def send_full_logs(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
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
    if tools.admin_check(bot, message):
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
            for msg in tools.split(last_logs):
                message.reply(msg)
        else:
            message.reply("Логи не найдены.")


@AutoConfigurator.on_message(Filters.command(commands=["list", "sources_list"]) & Filters.private)
def source_list(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
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
    if tools.admin_check(bot, message):
        if len(message.command) > 1:
            bot.reload_config()
            section = bot.remove_config_section(message.command[1])
            info = messages.SECTION_DELETED.format(section)
            message.reply(info)
        else:
            message.reply(messages.REMOVE)


@AutoConfigurator.on_message(Filters.command(commands=["add"]) & Filters.private)
def add_source(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
        if len(message.command) >= 3:
            bot.reload_config()
            section = bot.add_config_section(*message.command[1:])
            info = "Источник {0[0]} был добавлен.".format(section)
            message.reply(info)
        else:
            message.reply(messages.ADD)


@AutoConfigurator.on_message(Filters.command(commands=["settings"]) & Filters.private)
def settings(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
        bot.reload_config()
        info, reply_markup = tools.generate_setting_info(bot, "global")
        message.reply(info, reply_markup=reply_markup)


@AutoConfigurator.on_message(Filters.command(commands=["get_config"]) & Filters.private)
def get_config(bot: AutoConfigurator, message: Message):
    if tools.admin_check(bot, message):
        message.reply("Конфигурация бота:\n```{}```".format(open(bot.config_path).read()))
        message.reply_document(document=bot.config_path, caption="Файл конфигурации бота.")


@AutoConfigurator.on_message(Filters.command(commands=["about"]) & Filters.private)
def about(_, message: Message):
    message.reply(messages.ABOUT, disable_web_page_preview=True)


@AutoConfigurator.on_message(Filters.command(commands=["get_id"]))
def get_id(_, message: Message):
    message.reply("Chat id is `{}`".format(message.chat.id))


@AutoConfigurator.on_message(Filters.forwarded)
def get_forward_id(_, message: Message):
    if message.forward_from:
        id_ = message.forward_from.id
    else:
        id_ = message.forward_from_chat.id
    message.reply("Channel (user) ID is `{}`".format(id_))
