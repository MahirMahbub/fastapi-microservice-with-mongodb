from fastapi import APIRouter

from auth_app.utils.logger import get_logger
from auth_app.utils.tasks import send_account_verify_email

test_router: APIRouter = APIRouter()
logger = get_logger()


@test_router.get("/hello/{name}")
def say_hello(name: str) -> dict[str, str]:
    logger.info("Testing Route")
    send_account_verify_email.delay("mahirmahbub7@gmail.com", "It is a great token")
    return {"message": f"Hello {name}"}
