from asyncer import syncify, asyncify
from fastapi import APIRouter

# from auth_app.config.config import Settings
from auth_app.utils.email import EmailGenerator

from auth_app.utils.tasks import send_account_verify_email
test_router = APIRouter()


@test_router.get("/hello/{name}")
def say_hello(name: str):

    send_account_verify_email.delay("mahirmahbub7@gmail.com", "It is a great token")
    return {"message": f"Hello {name}"}
