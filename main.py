import uvicorn
from fastapi import FastAPI

# from auth_app.config.config import Settings
from auth_app.main import auth_app

# settings =Settings()

PORT = 8000
BIND = '127.0.0.1'
WORKERS = 10
RELOAD = True
app = FastAPI(
    title="SkillMatrix",
    description="Skill Matrix Application",
    version="1.0.0")
app.mount("/auth", auth_app)
if __name__ == "__main__":
    # install_packages()
    # uvicorn.run("hello:app", host=BIND, port=int(PORT), reload=RELOAD, debug=RELOAD, workers=int(WORKERS))
    uvicorn.run("main:app", host=BIND, port=int(PORT), reload=RELOAD, workers=int(WORKERS), env_file='.env')
