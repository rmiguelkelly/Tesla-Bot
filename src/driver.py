
from api import OnlineProductRetriever

from dbcontext import ProductDatabase
from product import Product

import smtplib

if (__name__ == '__main__'):

    retriever = OnlineProductRetriever()

    #  Search for products in this path
    retriever.set_paths([
        '/category/charging',
        '/category/vehicle-accessories',
        '/category/apparel',
        '/category/lifestyle'
    ])

    website_products = retriever.retrieve_all()
    print('Found {} products online'.format(len(website_products)))

    if len(website_products) == 0:
        print('No products found, maybe an error happened?')
    
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

    #  Handle the notification here
    print(len(new_products))

    #  Add the new products to the database
    db_context.update_database(new_products)