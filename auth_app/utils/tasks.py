import os

from celery import Celery

from auth_app.utils.email import EmailGenerator

celery_app = Celery(
    "worker",
    backend="redis://:password123@redis:6379/0",
    broker="amqp://user:bitnami@rabbitmq:5672//"
)
celery_app.conf.task_routes = {
    "auth_app.utils.tasks.*": "send_auth_email"}

celery = celery_app


@celery_app.task(acks_late=True)
def send_account_verify_email(email, token):
    email_handler = EmailGenerator()
    email_handler.get_account_verify_email(to_email=email,
                                           url=os.getenv("FRONT_END_URL") + "?user_verify=" + token)


@celery_app.task(acks_late=True)
def send_account_reset_password_email(email, token):
    email_handler = EmailGenerator()
    email_handler.get_account_change_password_email(to_email=email,
                                                    url=os.getenv(
                                                        "FRONT_END_URL") + "?reset_password=" + token)
