import asyncio
import logging
import handlers

from aiogram import Bot, Dispatcher
from config_data.config import create_config, Config
from db.requests import async_main, async_session
from middlewares.db import DataBaseSession


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(filename)s:%(lineno)d #%(levelname)-8s '
                        '[%(asctime)s] - %(name)s - %(message)s')
    logger.info("Starting bot...")

    await async_main()

    config: Config = create_config(".env")

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher()

    dp.include_router(handlers.user_router)
    dp.include_router(handlers.other_router)

    dp.update.middleware(DataBaseSession(session_pool=async_session))

    await bot.delete_webhook()
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")