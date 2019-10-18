import sys
sys.path.append('../')
import configparser
import telebot
from telegram.utils.request import Request
from telegram import Bot
from telebot import apihelper
import commands
from loguru import logger
from vk_api import VkApi
from handlers import *

warn_message = 'Невозможно прочитать конфигурацию бота TG_AutoPoster. ' \
               'В следствии этого не будут работать команды /list /sources_list /remove /add /get_config'


def main():
    # Чтение конфигурации бота из файла config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Настройка прокси, если указано в конфиге
    if config.get('DEFAULT', 'proxy_url', fallback=None):
        apihelper.proxy = {'https': config.get('DEFAULT', 'proxy_url')}
        request = Request(proxy_url=config.get('DEFAULT', 'proxy_url'), connect_timeout=15.0, read_timeout=15.0)
    else:
        request = None
    # Инициализация Telegram бота
    bot_token = config.get('DEFAULT', 'bot_token')
    bot = telebot.TeleBot(bot_token)
    sender_bot = Bot(bot_token, request=request)
    # Чтение из конфига логина и пароля ВК
    vk_login = config.get('DEFAULT', 'login')
    vk_pass = config.get('DEFAULT', 'pass')
    # Инициализация ВК сессии
    session = VkApi(login=vk_login, password=vk_pass, auth_handler=auth_handler, captcha_handler=captcha_handler,
                    config_filename='../vk_config.v2.json')
    session.auth()
    api_vk = session.get_api()

    admin_id = config.getint('DEFAULT', 'admin_id')
    bot_config_path = config.get('DEFAULT', 'bot_config_path')
    bot_logs_folder_path = config.get('DEFAULT', 'bot_logs_folder_path')

    commands.setup(bot, admin_id, bot_config_path, bot_logs_folder_path, session, api_vk, sender_bot)
    try:
        configparser.ConfigParser().read_file(open(bot_config_path, 'r', encoding='utf-8'))
    except FileNotFoundError:
        logger.warning(warn_message)
        bot.send_message(admin_id, warn_message)
    bot.infinity_polling(none_stop=True)


if __name__ == '__main__':
    if sys.platform == 'linux' and ('--daemon' in sys.argv or '-d' in sys.argv):
        import daemon
        import daemon.pidfile

        with daemon.DaemonContext(working_directory='.', pidfile=daemon.pidfile.PIDLockFile('TG_AutoConfigurator.pid')):
            logger.add('./logs/bot_log_{time}.log')
            logger.info('Запуск бота в режиме демона. PID процесса хранится в файле TG_AutoConfigurator.pid')
            main = logger.catch(main)
            main()
    else:
        logger.add('./logs/bot_log_{time}.log')
        main = logger.catch(main)
        main()
