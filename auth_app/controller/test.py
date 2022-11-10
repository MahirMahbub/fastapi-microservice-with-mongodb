from fastapi import APIRouter

# from auth_app.config.config import Settings
from auth_app.utils.email import EmailGenerator

test_router = APIRouter()


@test_router.get("/hello/{name}")
async def say_hello(name: str):

    return {"message": f"Hello {name}"}
