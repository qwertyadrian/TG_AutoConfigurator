from pyrogram import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from ..TG_AutoConfigurator import AutoConfigurator
from ..utils import messages


@AutoConfigurator.on_inline_query()
def inline(bot: AutoConfigurator, query: InlineQuery):
    string = query.query.lower()

    results = []

    bot.reload_config()
    sources_list = bot.config.sections()[3:] if bot.config.has_section("proxy") else bot.config.sections()[2:]

    for source in sources_list:
        if not string or source.startswith(string):
            text = messages.INLINE_INPUT_MESSAGE_CONTENT.format(
                source,
                bot.config.get(source, "channel"),
                bot.config.get(source, "last_id", fallback=0),
                bot.config.get(source, "last_story_id", fallback=0),
                bot.config.get(source, "pinned_id", fallback=0),
            )
            results.append(InlineQueryResultArticle(title=source, input_message_content=InputTextMessageContent(text)))

    query.answer(results=results, cache_time=0)
