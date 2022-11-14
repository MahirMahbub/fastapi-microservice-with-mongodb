import os

from celery import Celery

from auth_app.utils.email import EmailGenerator

celery_app = Celery(
    "email-worker",
    backend="redis://:Pass@123@auth_redis:6379/0",
    broker="amqp://user:Pass@123@auth_rabbitmq:5672//"
)
celery_app.conf.task_routes = {
    "auth_app.utils.tasks.send_account_verify_email": "send_verify_email",
    "auth_app.utils.tasks.send_account_reset_password_email": "send_change_password_email"}

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
