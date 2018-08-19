from django.db import models
from django.utils import timezone

from operation.util import auxiliary
from .management.managers import TransactionManager


class Transaction(models.Model):
    TRANSFER_METHODS = [
        ('ATM', 'ATM/Cash'),
        ('WIRE', 'Wire Transfer'),
        ('CHECK', 'Check'),
        ('MONEY_ORDER', 'Money Order'),
        ('CARD', 'Card'),
        ('ONLINE', 'Online')
    ]

    SPENDING_CATEGORIES = [
        ('UTILITIES', 'Utilities'),
        ('GROCERIES', 'Groceries'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('DINING', 'Dining'),
        ('TRAVEL', 'Travel'),
        ('MEDICAL', 'Medical'),
        ('MISC', 'Miscellaneous'),
        ('INCOME', 'Income'),
    ]

    identifier = models.CharField(max_length=20, unique=True,
                                  primary_key=True, default=auxiliary.make_id)
    customer_id = models.CharField(max_length=20, null=False,
                                   blank=False)

    amount = models.DecimalField(null=False, blank=False,
                                 decimal_places=2, max_digits=32)
    category = models.CharField(max_length=30, choices=SPENDING_CATEGORIES)

    transfer_time = models.DateTimeField(null=False, default=timezone.now,
                                         editable=False)
    transfer_method = models.CharField(max_length=30, choices=TRANSFER_METHODS)

    objects = TransactionManager()

    class Meta:
        ordering = ['-transfer_time']
