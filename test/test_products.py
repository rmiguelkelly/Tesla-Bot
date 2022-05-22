import unittest
from src.product import Product

class ProductTestCase(unittest.TestCase):

    def test_product_dataclass_equality(self):

        # Tests for dataclass equality
        product1 = Product('test_id', 'test_str', 'test_price', 'test_link', 'test_catagory')
        product2 = Product('test_id', 'test_str', 'test_price', 'test_link', 'test_catagory')

        self.assertEqual(product1, product2)

    def test_product_dataclass_hashing(self):

        # Tests for dataclass equality
        product1 = Product('test_id', 'test_str1', 'test_price1', 'test_link1', 'test_catagory1')
        product2 = Product('test_id', 'test_str2', 'test_price2', 'test_link2', 'test_catagory2')

        # The two classes should not be equal but their hashes should
        self.assertNotEqual(product1, product2)
        self.assertEqual(hash(product1), hash(product2))