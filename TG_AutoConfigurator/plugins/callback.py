from configparser import NoSectionError

from pyrogram import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import tools, messages


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
            return

        elif data[0] == "switch":
            bot.reload_config()
            option = bot.config.getboolean(
                data[1],
                data[2],
                fallback=bot.config.getboolean(
                    "global", data[2], fallback=True if data[2] in ("disable_web_page_preview", "sign_posts") else False
                ),
            )
            if (
                data[1] != "global"
                and bot.config.has_option(data[1], data[2])
                and option
                is not bot.config.getboolean(
                    "global", data[2], fallback=True if data[2] in ("disable_web_page_preview", "sign_posts") else False
                )
            ):
                bot.config.remove_option(data[1], data[2])
            else:
                bot.config.set(data[1], data[2], str(not option))
            bot.save_config()
            info, reply_markup = tools.generate_setting_info(bot, data[1])
            callback_query.edit_message_text(info, reply_markup=reply_markup, disable_web_page_preview=True)
            return

        elif data[0] == "show":
            bot.reload_config()
            if data[2] == "send_reposts":
                info = "**Настройка отправки репостов:**\n\n"
                button_list = [
                    InlineKeyboardButton("Отключить", callback_data="reposts {} no".format(data[1])),
                    InlineKeyboardButton("Включить", callback_data="reposts {} yes".format(data[1])),
                ]
                footer_buttons = [
                    InlineKeyboardButton("Только посты", callback_data="reposts {} post_only".format(data[1]))
                ]
                button_list = tools.build_menu(button_list, n_cols=2, footer_buttons=footer_buttons)
                if data[1] != "global":
                    button_list.append(
                        [
                            InlineKeyboardButton(
                                "Использование глобальное значение", callback_data="reposts {} reset".format(data[1])
                            )
                        ]
                    )
                if bot.config.has_option(data[1], data[2]):
                    option = bot.config.get(data[1], "send_reposts")
                else:
                    option = bot.config.get("global", "send_reposts")
                    info = (
                        "Этот источник использует общие настройки отправки репостов (См. в /settings)."
                        "Измения настроек здесь приведет к их переопределению\n"
                    )
                if option in ("no", "False", 0):
                    info += "Отправка репостов отключена"
                elif option in ("post_only", 1):
                    info += "Отправка только постов" + messages.PARTIAL_REPOSTS
                elif option in ("yes", "all", "True", 2):
                    info += "Отправка репостов включена"
                reply_markup = InlineKeyboardMarkup(button_list)
                callback_query.edit_message_text(info, reply_markup=reply_markup)
                return

        elif data[0] == "reposts":
            if data[2] == "reset" and bot.config.has_option(data[1], "send_reposts"):
                bot.config.remove_option(data[1], "send_reposts")
            else:
                bot.config.set(data[1], "send_reposts", data[2])
            bot.save_config()

        info, reply_markup = tools.generate_setting_info(bot, data[1])
        callback_query.edit_message_text(info, reply_markup=reply_markup, disable_web_page_preview=True)
