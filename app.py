import asyncio
import logging

logging.basicConfig()
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("slack_bolt").setLevel(logging.INFO)
logging.getLogger("lsimons_bot").setLevel(logging.DEBUG)


if __name__ == "__main__":
    from lsimons_bot.app.main import main

    asyncio.run(main())
