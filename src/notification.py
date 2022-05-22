
import smtplib
import os

from product import Product

#  Handle any notification that need to sent out
class NotificationSystem:
    
    def __init__(self) -> None:
        pass

    #  Self-notification
    def post_admin_email(self, subject:str, body:str):

        #  Handle credentials through .env or external enviroment
        email = os.environ['ADMIN_EMAIL']
        host = os.environ['SMTP_ENDPOINT']
        port = os.environ['SMTP_PORT']
        username = os.environ['SMTP_USERNAME']
        password = os.environ['SMTP_PASSWORD']

        client = smtplib.SMTP(host, port, timeout=5)
        client.starttls()
        client.login(username, password)

        message = """\
        Subject: {}\r\n
        {}.""".format(subject, body)

        client.sendmail('no-reply@ronanmiguelkelly.com', email, message)

        client.close()
        pass


    def post_twitter(self, products:set[Product]):
        pass

