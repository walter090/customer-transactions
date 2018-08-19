from django.test import TestCase
from .models import Transaction


class TransactionTest(TestCase):
    def test_creation(self):
        entertainment_counts = Transaction.objects.filter(category='ENTERTAINMENT').count()
        Transaction.objects.create(customer_id='000',
                                   amount='300.00',
                                   category='ENTERTAINMENT',
                                   transfer_method='CARD')

        self.assertEqual(Transaction.objects.filter(category='ENTERTAINMENT').count(),
                         entertainment_counts + 1)
