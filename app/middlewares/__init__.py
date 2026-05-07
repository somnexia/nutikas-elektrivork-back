from fastapi import FastAPI

from app.middlewares.auth_middleware import AuthMiddleware


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        AuthMiddleware,
        open_paths=["/auth/register", "/auth/refresh"],
    )