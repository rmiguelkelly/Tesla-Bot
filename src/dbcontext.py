
from datetime import date
from os import path, unlink
import sqlite3
from typing import Optional

from product import Product

"""
 Product
 -  id       | string (unique)
 -  name     | string
 -  price    | string
 -  link     | string
 -  category | string (enum)
"""
 
class ProductDatabase:

    #  Constant name of the database 
    def database_name(self) -> str:
        return 'products.db'

    #  Does the physical database file exist
    def database_exists(self):
        return path.exists(self.database_name())

    #  Creates the database if it doesnt exist, drops and re-creates the tables, and seeds it with data
    def seed(self, products: set[Product] = set()):

        connection = sqlite3.connect(self.database_name())
        
        connection.execute('DROP TABLE IF EXISTS products')

        query_create = 'CREATE TABLE products (id primary key, name, price, link, category, last_updated)'
        connection.execute(query_create)

        for prod in products:
            query_insert = 'INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)'
            values = (prod.id, prod.name, prod.price, prod.link, prod.category, date.today())
            connection.execute(query_insert, values)

        connection.commit()
        connection.close()
    
    #  Delete the database, resets everything
    def reset(self):
        unlink(self.database_name())

    #  Return a set of all products in the database
    def all_products(self) -> dict[str, Product]:

        connection = sqlite3.connect(self.database_name())
        curser = connection.execute('SELECT * FROM products')

        records = curser.fetchall()

        database_products = dict[str, Product]()

        for (id, name, price, link, category, _) in records:
            db_product = Product(id, name, price, link, category)
            database_products[id] = db_product

        connection.close()

        return database_products

    #  Inserts a new product
    def update_database(self, products:set[Product]):

        conn = sqlite3.connect(self.database_name())

        for prod in products:
            query_insert = 'INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)'
            values = (prod.id, prod.name, prod.price, prod.link, prod.category, date.today())
            conn.execute(query_insert, values)

        conn.commit()
        conn.close()

    #  Updates the database with products that have changed
    def update_changed_products(self, changes:set[(Product, Product)]):

        conn = sqlite3.connect(self.database_name())
        
        for diff in changes:
            new = diff[1]
            update_query = "UPDATE products SET name=?, price=?, link=?, category=?, last_updated=? WHERE id=?"
            values = (new.name, new.price, new.link, new.category, date.today(), new.id)
            conn.execute(update_query, values)
            
        conn.commit()
        conn.close()
