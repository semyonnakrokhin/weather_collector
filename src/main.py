import asyncio

from config import Settings
from di_container import Application
from master import MasterService


def create_master_service() -> MasterService:
    settings_dict = Settings().model_dump()
    application = Application()
    application.config.from_dict(settings_dict)

    master_service = application.master.master_service_provider()
    return master_service


async def main():
    master_service = create_master_service()
    await master_service.start()


if __name__ == "__main__":
    asyncio.run(main())
