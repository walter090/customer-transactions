import os
from decimal import Decimal

from django.test import TestCase, Client
from .models import Customer


class CustomerTest(TestCase):
    def setUp(self):
        self.client = Client()

        Customer.objects.create(username='john123',
                                email='john123@fake.com',
                                first_name='john',
                                last_name='smith',
                                birth_year=1976,
                                occupation_type='MISC',
                                balance=300,
                                password='john_secret')

    def test_customer(self):
        response = self.client.post(path='/customers/',
                                    data={
                                        'username': 'jim123',
                                        'email': 'jim123@fake.com',
                                        'first_name': 'jim',
                                        'last_name': 'smith',
                                        'birth_year': 1976,
                                        'occupation_type': 'MISC',
                                        'balance': 300,
                                        'password': 'john_secret'
                                    })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Customer.objects.filter(username='jim123').count(), 1)

    def test_retrieval(self):
        customer = Customer.objects.get(username='john123')
        customer_id = customer.identifier
        response = self.client.get(path=os.path.join('/customers/', customer_id, ''))
        self.assertEqual(response.status_code, 200)

    def test_transfer(self):
        customer = Customer.objects.get(username='john123')
        customer_id = customer.identifier

        response = self.client.post(path='/customers/transfer/',
                                    data={'customer_id': customer_id,
                                          'amount': -50.99})

        customer = Customer.objects.get(username='john123')

        self.assertEqual(customer.balance, Decimal('249.01'))
        self.assertEqual(response.status_code, 200)
