import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from asyncer import asyncify, syncify
from jinja2 import Environment, select_autoescape, FileSystemLoader

# from auth_app.config.config import Settings


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class EmailGenerator(metaclass=SingletonMeta):

    def __init__(self):
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.gmail_port = os.getenv("GMAIL_PORT")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.tls = os.getenv("TLS")

    def send_email(self, to, subject, body):
        sender_address = self.sender_email
        sender_pass = self.sender_password
        receiver_address = to
        # Setup the MIME
        message = MIMEMultipart("alternative")
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = subject
        message.attach(MIMEText(body, 'html'))
        session = smtplib.SMTP('smtp.gmail.com', 587)
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
        print('Mail Sent')

    def get_account_verify_email(self, to_email, **kwargs):
        template = self.get_jinja_template(template_name='verify_email.html')
        self.send_email(to_email, "Verify Account", template.render(**kwargs))

    def get_account_change_password_email(self, to_email='mahirmahbub7@gmail.com', **kwargs):
        template = self.get_jinja_template(template_name='reset_password.html')
        self.send_email(to_email, "Reset Password", template.render(**kwargs))

    @staticmethod
    def get_jinja_template(template_name):
        env = Environment(
            loader=FileSystemLoader(searchpath='auth_app/static/template/'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(template_name)
        return template

