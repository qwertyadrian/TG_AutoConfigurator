from pyrogram import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultArticle,
                      InputTextMessageContent)

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import messages, tools


@AutoConfigurator.on_inline_query()
def inline(bot: AutoConfigurator, query: InlineQuery):
    if tools.admin_check(bot, query):
        string = query.query.lower()

        results = []

        bot.reload_config()
        sources_list = bot.config.sections()[3:] if bot.config.has_section("proxy") else bot.config.sections()[2:]

        for source in sources_list:
            if not string or source.startswith(string):
                button_list = []
                text = messages.INLINE_INPUT_MESSAGE_CONTENT.format(
                    source,
                    bot.config.get(source, "channel"),
                    bot.config.get(source, "last_id", fallback=0),
                    bot.config.get(source, "last_story_id", fallback=0),
                    bot.config.get(source, "pinned_id", fallback=0),
                )
                button_list.append(InlineKeyboardButton("Удалить источник", callback_data="delete " + source))
                reply_markup = InlineKeyboardMarkup(tools.build_menu(button_list))
                results.append(
                    InlineQueryResultArticle(
                        title=source,
                        input_message_content=InputTextMessageContent(text, disable_web_page_preview=True),
                        reply_markup=reply_markup,
                    )
                )

        query.answer(results=results, cache_time=0)
