import asyncio
import logging
from bot.bot import main

# log_file = '/www/telega_bot/sport_telegram_bot/log/bot.log'

if __name__ == "__main__":
    try:
        logging.basicConfig(
            # filename=log_file,
            # filemode='a',
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )
        asyncio.run(main())
    except Exception as err:
        print(err)
