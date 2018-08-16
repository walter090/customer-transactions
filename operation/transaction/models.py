from django.db import models
from django.utils import timezone

from operation.util import auxiliary
from .management.enums import MethodOfTransaction, SpendingCategory


class Transaction(models.Model):
    identifier = models.BigIntegerField(unique=True, primary_key=True, default=auxiliary.make_id)

    amount = models.IntegerField(null=False, blank=False)
    category = models.CharField(max_length=30,
                                choices=[(key, key.value for key in SpendingCategory)])

    transfer_time = models.DateTimeField(null=False, default=timezone.now, editable=False)
    transfer_method = models.CharField(max_length=30,
                                       choices=[(key, key.value for key in MethodOfTransaction)])

    class Meta:
        ordering = ['-transfer_time']
