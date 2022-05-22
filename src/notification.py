
import smtplib
import os
from typing import Optional
import tweepy

from product import Product

#  Handle any notification that need to sent out
class NotificationSystem:

    client:Optional[tweepy.Client] = None

    def authenticate_twitter_api():
        if NotificationSystem.client is not None:
            # Already authenticated...
            return

        api_key = os.environ['TWITTER_API_KEY']
        api_secret = os.environ['TWITTER_API_SECRET']
        access_token = os.environ['TWITTER_ACCESS_TOKEN']
        access_secret = os.environ['TWITTER_ACCESS_SECRET']

        # Attempt to authenticate
        NotificationSystem.client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
            wait_on_rate_limit=True
        )

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

        message = "Subject: {}\r\n\r\n{}.".format(subject, body)

        client.sendmail('no-reply@ronanmiguelkelly.com', email, message)

        client.close()

        # Generic post tweet
    def post_twitter(self, tweet:str):

        if len(tweet) == 0:
            # empty tweet
            return
        
        try: 
            twitter_res = NotificationSystem.client.create_tweet(text=tweet)
            print(twitter_res.data)
        except Exception as err:
            print("Error sending tweet: {}".format(err))


