import configparser
import telebot
import sys
import commands
from loguru import logger

warn_message = 'Невозможно прочитать конфигурацию бота TG_AutoPoster. ' \
                'Вследвии этого не будут работать команды /list /sources_list /remove /add /get_config'


def main():
    # Чтение конфигурации бота из файла config.ini
    config = configparser.ConfigParser()
    config.read_file(open('config.ini', 'r', encoding='utf-8'))
    # Инициализация Telegram бота
    bot_token = config.get('DEFAULT', 'bot_token')
    bot = telebot.TeleBot(bot_token)

    admin_id = config.getint('DEFAULT', 'admin_id')
    bot_config_path = config.get('DEFAULT', 'bot_config_path')
    bot_logs_folder_path = config.get('DEFAULT', 'bot_logs_folder_path')

    commands.setup(bot, admin_id, bot_config_path, bot_logs_folder_path)
    try:
        configparser.ConfigParser().read_file(open(bot_config_path, 'r', encoding='utf-8'))
    except FileNotFoundError:
        logger.warning(warn_message)
        bot.send_message(admin_id, warn_message)
    bot.infinity_polling(none_stop=True)


if __name__ == '__main__':
    if sys.platform == 'linux':
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
