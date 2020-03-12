from loguru import logger

from .TG_AutoConfigurator import AutoConfigurator, create_parser

if __name__ == "__main__":
    args = create_parser().parse_args()
    logger.add("./logs/TG_AutoConfigurator_log_{time}.log")
    bot = AutoConfigurator(args.config, args.ipv6)
    bot.run()
