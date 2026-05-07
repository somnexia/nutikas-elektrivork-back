from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.mongo import close_mongo, connect_to_mongo
from app.middlewares import setup_middlewares
from app.routes import router



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения: запуск и завершение."""
    await connect_to_mongo()
    yield
    await close_mongo()



def create_app() -> FastAPI:
    """Создаёт и конфигурирует экземпляр FastAPI приложения."""
    app = FastAPI(lifespan=lifespan)

    setup_middlewares(app)
    app.include_router(router)

    return app

