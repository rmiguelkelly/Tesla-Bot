from api import OnlineProductRetriever
from dbcontext import ProductDatabase
from notification import NotificationSystem
from product import Product

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

def notify_admin_new_products(products:set[Product]):

    message = 'New Tesla Products Found\n\n'

    for product in products:
        product_str = '{} - {}\n{}'.format(product.name, product.price, product.link)
        message += product_str
        message += '\n'
        message += '-------------------------'
        message += '\n'

    message += 'Thats All Folks!'

    notify = NotificationSystem()
    notify.post_admin_email('{} New Products Found'.format(len(products)), message)
    

if (__name__ == '__main__'):

    #  Initiate and retrieve all products on the website
    retriever = create_product_retriever()
    website_products = retriever.retrieve_all()
    print('Found {} products online'.format(len(website_products)))

    #  If no products were found, an error may have occured
    if len(website_products) == 0:
        NotificationSystem().post_admin_email('Error', 'An error occured, thake this L')
        print('No products found, maybe an error happened?')
        pass
    
    #  The cached products from the initial seeding + updates
    db_context = ProductDatabase()
    
    #  No products, seed the database
    if not db_context.database_exists():
        print('Database not found, creating and seeding database')
        db_context.seed(website_products)
    
    #  All the products from the database
    db_products = db_context.all_products()

    new_products = set[Product]()

    #  All products from the website that are not in the database
    for product in website_products:

        #  If this product from the website is NOT in the database, it must be a new one
        if product not in db_products:
            new_products.add(product)

    print("----- New Products -----")
    for new_product in new_products:
        print(new_product.name)

    #  For any new products, notify the admin plus subscribers
    if len(new_products) > 0:

        #  Perform the notifications
        notify_admin_new_products(new_products)

        #  Add the new products to the database
        db_context.update_database(new_products)