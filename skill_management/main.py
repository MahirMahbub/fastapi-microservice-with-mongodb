import os

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from skill_management.config.config import initiate_database
from skill_management.controllers.router import api_router
from skill_management.utils.logger import get_logger

# API Doc
if os.getenv("ENVIRONMENT") == "local":
    skill_app = FastAPI(
        title="SkillManagementApp",
        description="Skill Management Application",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        # root_path="/api/v1"
    )
else:
    skill_app = FastAPI(
        title="SkillManagementApp",
        description="Skill Management Application",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        debug=True
        # root_path="/api/v1"
    )
skill_app.add_middleware(GZipMiddleware)
skill_app.include_router(api_router, prefix='/api/v1')


@skill_app.on_event("startup")
async def start_database() -> None:
    logger = get_logger()
    logger.info("Initiating database........")
    await initiate_database()
    logger.info("Initiating database completed........")

#
# PORT = 8000
# BIND = '127.0.0.1'
# WORKERS = 10
# RELOAD = True
# app = FastAPI(
#     title="SkillMatrix",
#     description="Skill Matrix Application",
#     version="1.0.0")
# # app.mount("/auth", auth_app)
# if __name__ == "__main__":
#     # install_packages()
#     # uvicorn.run("hello:app", host=BIND, port=int(PORT), reload=RELOAD, debug=RELOAD, workers=int(WORKERS))
#     uvicorn.run("auth_app.main:auth_app", host=BIND, port=int(PORT), reload=RELOAD, workers=int(WORKERS))
