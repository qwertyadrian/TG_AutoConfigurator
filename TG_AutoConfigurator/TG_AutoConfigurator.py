import argparse
import configparser
import os
from typing import Tuple

from loguru import logger
from pyrogram import Client

CONFIG_PATH = os.path.join(os.getcwd(), "config.ini")
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
        default=CONFIG_PATH,
        help="Путь к конфиг файлу бота TG_AutoPoster (по умолчанию {})".format(CONFIG_PATH),
    )

    return parser


class AutoConfigurator(Client):
    def __init__(self, config_file=CONFIG_PATH, ipv6=False):
        self.config_path = config_file
        self.config = configparser.ConfigParser()

        self.reload_config()

        self.admin_id = self.config.getint("global", "admin_id")
        self.bot_logs_folder_path = os.path.join(".", "logs")

        super().__init__(
            "TG_AutoConfigurator",
            config_file=config_file,
            ipv6=ipv6,
            plugins=dict(root=PLUGINS_PATH),
            workdir="."
        )

        self.set_parse_mode("markdown")

    def add_config_section(self, domain: str, chat_id: str, last_id: str = "0") -> Tuple[str, str, str]:
        domain = domain.replace("https://vk.com/", "").replace("https://m.vk.com/", "")
        self.config.add_section(domain)
        self.config.set(domain, "channel", chat_id)
        self.config.set(domain, "last_id", last_id)
        self.save_config()
        return domain, chat_id, last_id

    def remove_config_section(self, section: str) -> Tuple[str, str, str]:
        channel = self.config.get(section, "channel")
        last_id = self.config.get(section, "last_id")
        self.config.remove_section(section)
        self.save_config()
        return section, channel, last_id

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            self.config.write(f)
        logger.debug("Config saved.")

    def reload_config(self):
        self.config.clear()
        self.config.read(self.config_path)
        logger.debug("Config reloaded.")
