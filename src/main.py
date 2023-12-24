import asyncio

from di_container import Application


async def main():
    application = Application()

    master_service = application.master.master_service()
    await master_service.start()


if __name__ == "__main__":
    asyncio.run(main())
