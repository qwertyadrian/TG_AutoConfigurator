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
        elif data[0] == "switch":
            bot.reload_config()
            if data[1] != "send_reposts":
                option = bot.config.getboolean("global", data[1])
                bot.config.set("global", data[1], str(not option))
            else:
                option = bot.config.get("global", "send_reposts")
                if option in ("no", "False", 0):
                    bot.config.set("global", data[1], "post_only")
                elif option in ("post_only", 1):
                    bot.config.set("global", data[1], "all")
                elif option in ("yes", "all", "True", 2):
                    bot.config.set("global", data[1], "no")
            bot.save_config()
            info, reply_markup = tools.generate_setting_info(bot)
            callback_query.edit_message_text(info, reply_markup=reply_markup)
