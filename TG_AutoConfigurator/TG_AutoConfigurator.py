import argparse
import configparser
import os
from typing import Tuple

from loguru import logger
from pyrogram import Client

BOT_PATH = os.getcwd()
PLUGINS_PATH = os.path.join(os.path.relpath(os.path.dirname(__file__)), "plugins")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="TG_AutoConfigurator",
        description="Telegram Bot for configuring auto posting from VK",
        epilog="(C) 2018-2020 Adrian Polyakov\nReleased under the MIT License.",
    )

    parser.add_argument(
        "-6", "--ipv6", action="store_true", help="Использовать IPv6 при подключении к Telegram (IPv4 по умолчанию)"
    )

    parser.add_argument(
        "-c",
        "--config",
        default=BOT_PATH,
        help="Путь к папке с ботом TG_AutoPoster (по умолчанию {})".format(BOT_PATH),
    )

    return parser


class AutoConfigurator(Client):
    def __init__(self, bot_path=BOT_PATH, ipv6=False):
        if "config.ini" in bot_path:
            self.bot_path = os.path.dirname(bot_path)
        else:
            self.bot_path = bot_path

        self.config_file = os.path.join(self.bot_path, "config.ini")
        self.bot_logs_folder_path = os.path.join(self.bot_path, "logs")

        self.config = configparser.ConfigParser()
        self.reload_config()

        self.admin_id = self.config.getint("global", "admin_id")

        super().__init__(
            "TG_AutoConfigurator",
            config_file=self.config_file,
            ipv6=ipv6,
            plugins=dict(root=PLUGINS_PATH),
            workdir="."
        )

        self.set_parse_mode("markdown")

    def add_config_section(
        self, domain: str, chat_id: str, last_id: str = "0", pinned_id: str = "0", last_story_id: str = "0"
    ) -> Tuple[str, str, str, str, str]:
        domain = domain.replace("https://vk.com/", "").replace("https://m.vk.com/", "")
        self.config.add_section(domain)
        self.config.set(domain, "channel", chat_id)
        self.config.set(domain, "last_id", last_id)
        self.config.set(domain, "pinned_id", pinned_id)
        self.config.set(domain, "last_story_id", last_story_id)
        self.save_config()
        return domain, chat_id, last_id, pinned_id, last_story_id

    def remove_config_section(self, section: str) -> Tuple[str, str, str, str, str]:
        channel = self.config.get(section, "channel")
        last_id = self.config.get(section, "last_id", fallback=0)
        pinned_id = self.config.get(section, "pinned_id", fallback=0)
        last_story_id = self.config.get(section, "last_story_id", fallback=0)
        self.config.remove_section(section)
        self.save_config()
        return section, channel, last_id, pinned_id, last_story_id

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            self.config.write(f)
        logger.debug("Config saved.")

    def reload_config(self):
        self.config.clear()
        self.config.read(self.config_file)
        logger.debug("Config reloaded.")
