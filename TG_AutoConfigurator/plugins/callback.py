from configparser import NoSectionError

from pyrogram import CallbackQuery

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import tools


@AutoConfigurator.on_callback_query()
def callback(bot: AutoConfigurator, callback_query: CallbackQuery):
    if tools.admin_check(bot, callback_query):
        data = callback_query.data.split()
        if data[0] == "delete":
            bot.reload_config()
            try:
                section = bot.remove_config_section(data[1])
            except NoSectionError:
                info = "Источник {} не был найден. Возможно он был уже удален.".format(data[1])
            else:
                info = (
                    "Источник {0[0]} был удален.\nДля его восстановления используйте команду"
                    " `/add {0[0]} {0[1]} {0[2]}`".format(section)
                )
            callback_query.edit_message_text(info)
