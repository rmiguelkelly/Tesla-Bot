from logging.handlers import TimedRotatingFileHandler
from time import sleep
from xmlrpc.client import Boolean
from api import OnlineProductRetriever
from dbcontext import ProductDatabase
from notification import NotificationSystem
from product import Product
import logging
from os import environ, mkdir, path

#  Load the .env for testing
from dotenv import load_dotenv
load_dotenv()

#  Create and return the online product retriever
def create_product_retriever():

    retriever = OnlineProductRetriever()

    #  Search for products in this path
    retriever.set_paths([
        '/category/charging',
        '/category/vehicle-accessories',
        '/category/apparel',
        '/category/lifestyle'
    ])

    return retriever

def notify_admin_new_products(new_products:set[Product], changed_products: set[((Product, Product))]):

    message = 'New Tesla Products Found\n'
    message += '-------------------------\n'

    index = 1
    for product in new_products:
        product_str = '{}: {} - {} ({})'.format(index, product.name, product.price, product.link)
        message += product_str
        message += '\n'
        index += 1

    message += "\n\n"
    message += "Changed Products\n"
    message += '-------------------------'
    message += "\n"

    # Handle the changed procucts

    index = 1
    for diff in changed_products:
        old = diff[0]
        new = diff[1]

        # If the names are not equal or the prices are equal, omit this change
        if (old.name != new.name or old.price == new.price):
            continue

        message_diff = "{}: {} changed from {} to {} ({})".format(index, new.name, old.price, new.price, new.link)
        message += message_diff
        message += '\n'
        index += 1

    message += "\n"
    message += 'Thats All Folks!'

    email_subject = '{} New Products Found and {} Products Changed'.format(len(new_products), len(changed_products))

    notify = NotificationSystem()
    notify.post_admin_email(email_subject, message)
    
    # Log this instead
    logging.info(email_subject)

# Send the results to twitter
# This should be done syncronously with a small delay between each tweet
def tweet_results(new_products:set[Product], changed_products: set[((Product, Product))]):

    # Delay each tweet by some time in seconds
    tweet_delay = 2.0

    notification_handle = NotificationSystem()

    # Some shared footer for the tweets
    tweet_footer = 'Brought to you by @tesla_shop_bot'

    # Post the new products first
    for product in new_products:
        tweet = 'New product in the shop at #tesla\nGet it for {}\n{}\n{}\n{}'.format(product.name, product.price, product.link, tweet_footer)
        notification_handle.post_twitter(tweet)
        sleep(tweet_delay)
    
    # Post the changed products
    for (old, new) in changed_products:

        # For sanity, make sure the prices are actually different
        if old.price == new.price:
            continue

        tweet = '{} has changed from {} to {}\n{}\n{}'.format(new.name, old.price, new.price, new.link, tweet_footer)
        notification_handle.post_twitter(tweet)
        sleep(tweet_delay)

def initialize_logger():

    log_folder = 'logs/'

    if not path.exists(log_folder):
        mkdir(log_folder)

    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler = TimedRotatingFileHandler(filename='{}/applog'.format(log_folder), when='midnight', interval=1, backupCount=365)

    # Log format to use
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    formatter = logging.Formatter(log_format, datefmt='%m-%d %H:%M')
    console.setFormatter(formatter)
    root_logger.addHandler(console)

def valid_env() -> bool:
    env_var_keys = [
        'ADMIN_EMAIL',

        'SMTP_ENDPOINT',
        'SMTP_PORT',
        'SMTP_USERNAME',
        'SMTP_PASSWORD',

        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET',
    ]

    missing_key = False

    for key in env_var_keys:
        try:
            _ = environ[key]
        except:
            logging.error('Missing \'{}\' enviromental variable'.format(key))
            missing_key = True

    return not missing_key

if (__name__ == '__main__'):

    #  Create the log folder and the logger
    initialize_logger()

    if not valid_env():
        logging.critical('Application terminated because of missing enviroment variables')
        exit()

    #  Authenticate Twitter API
    NotificationSystem.authenticate_twitter_api()

    #  Initiate and retrieve all products on the website
    retriever = create_product_retriever()
    website_products = retriever.retrieve_all()
    logging.info('Found {} products online'.format(len(website_products)))

    #  If no products were found, an error may have occured
    if len(website_products) == 0:
        NotificationSystem().post_admin_email('Error', 'An error occured, take this L')
        logging.error('No products found, maybe an error happened?')
        exit()
    
    #  The cached products from the initial seeding + updates
    db_context = ProductDatabase()
    
    #  No products, seed the database
    if not db_context.database_exists():
        logging.info('Product database not found, creating and seeding database')
        db_context.seed(website_products)
    
    #  All the products from the database
    db_products = db_context.all_products()

    new_products = set[Product]()

    #  Set of the products that were changed (old, new)
    changed_products = set[(Product, Product)]()

    #  All products from the website that are not in the database
    for product in website_products:

        #  If this product from the website is NOT in the database, it must be a new one
        exists_in = product.id in db_products
        if not exists_in:
            new_products.add(product)
        else:
            #  If this product exists in the database but is not equal to the stored one
            if db_products[product.id] != product:
                changed_products.add((db_products[product.id], product))

    #  For any new products, notify the admin plus subscribers
    if len(new_products) > 0 or len(changed_products) > 0:

        #  Perform the notifications
        notify_admin_new_products(new_products, changed_products)

        #  Post the results to twitter
        tweet_results(new_products, changed_products)

        #  Add the new products to the database
        db_context.update_database(new_products)

        #  Update the changed products
        db_context.update_changed_products(changed_products)
    else:
        logging.info('No new products or changes found')