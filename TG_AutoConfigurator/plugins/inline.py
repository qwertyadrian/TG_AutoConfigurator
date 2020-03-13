from pyrogram import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import tools


@AutoConfigurator.on_inline_query()
def inline(bot: AutoConfigurator, query: InlineQuery):
    if tools.admin_check(bot, query):
        string = query.query.lower()

        results = []

        bot.reload_config()
        sources_list = bot.config.sections()[3:] if bot.config.has_section("proxy") else bot.config.sections()[2:]

        for source in sources_list:
            if not string or source.startswith(string):
                text, reply_markup = tools.generate_setting_info(bot, source)
                results.append(
                    InlineQueryResultArticle(
                        title=source,
                        input_message_content=InputTextMessageContent(text, disable_web_page_preview=True),
                        reply_markup=reply_markup,
                    )
                )

        query.answer(results=results, cache_time=0)
