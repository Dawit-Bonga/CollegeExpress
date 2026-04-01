from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.rate_limit import configure_rate_limiting
from app.routers.essays import router as essays_router
from app.routers.roadmaps import router as roadmaps_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI()

    configure_rate_limiting(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(roadmaps_router)
    app.include_router(essays_router)
    return app


app = create_app()
