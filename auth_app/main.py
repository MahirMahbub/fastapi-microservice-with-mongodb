import uvicorn
from fastapi import FastAPI

from auth_app.config.config import initiate_database
from auth_app.controller.router import api_router

# API Doc
auth_app = FastAPI(
    title="AuthApp",
    description="Authentication Application",
    version="1.0.0",
)

auth_app.include_router(api_router)


@auth_app.on_event("startup")
async def start_database():
    await initiate_database()


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
