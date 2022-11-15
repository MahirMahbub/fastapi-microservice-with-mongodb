import os

from fastapi import FastAPI
from auth_app.config.config import initiate_database
from auth_app.controller.router import api_router
from auth_app.utils.logger import get_logger

# API Doc
if os.getenv("ENVIRONMENT") == "local":
    auth_app = FastAPI(
        title="AuthApp",
        description="Authentication Application",
        version="1.0.0",
        openapi_url="/api/v1/auth/openapi.json",
        docs_url="/api/v1/auth/docs",
        # root_path="/api/v1"
    )
else:
    auth_app = FastAPI(
        title="AuthApp",
        description="Authentication Application",
        version="1.0.0",
        openapi_url="/api/v1/auth/openapi.json",
        docs_url="/api/v1/auth/docs",
        debug=True
        # root_path="/api/v1"
    )

auth_app.include_router(api_router, prefix='/api/v1/auth')


@auth_app.on_event("startup")
async def start_database():
    logger = get_logger()
    logger.info("Initiating database........")
    await initiate_database()
    logger.info("Initiating database completed........")


@auth_app.on_event("startup")
async def initiate_logger():
    pass

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
