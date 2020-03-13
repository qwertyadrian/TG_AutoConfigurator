from configparser import NoSectionError, NoOptionError

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
            if data[2] != "send_reposts":
                option = bot.config.getboolean(data[1], data[2], fallback=bot.config.getboolean("global", data[2]))
                bot.config.set(data[1], data[2], str(not option))
            else:
                option = bot.config.get(data[1], "send_reposts", fallback=bot.config.get("global", "send_reposts"))
                if option in ("no", "False", 0):
                    bot.config.set(data[1], "send_reposts", "post_only")
                elif option in ("post_only", 1):
                    bot.config.set(data[1], "send_reposts", "all")
                elif option in ("yes", "all", "True", 2):
                    bot.config.set(data[1], "send_reposts", "no")
            bot.save_config()
            info, reply_markup = tools.generate_setting_info(bot, data[1])
            callback_query.edit_message_text(info, reply_markup=reply_markup, disable_web_page_preview=True)
