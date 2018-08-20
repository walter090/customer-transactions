import os
from decimal import Decimal

import requests
from django.core.exceptions import ValidationError
from django.db.models import Manager

from .secret_constants import APIConsts
from requests.exceptions import HTTPError


class TransactionManager(Manager):
    def create(self, customer_id, amount,
               category, transfer_method, token=None):
        """ Create a new transaction, checks if the customer_id exists
        before saving to db.

        Args:
            customer_id: str, Customer identifier, pk.
            amount: str, Amount of transaction.
            category: str, Category of transaction.
            transfer_method: str, Method of transfer.
            token: str, OAuth token.

        Returns:
            None
        """
        amount = Decimal(amount)
        if amount == 0:
            raise ValidationError

        if not APIConsts.TESTING.value:
            url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, 'transfer', '')
            data = {'amount': amount, 'customer_id': customer_id}

            headers = {'Authorization': token} if token else {}

            response = requests.post(url=url, data=data, headers=headers)
            if response.status_code != requests.codes.ok:
                raise HTTPError(response)

        if category == 'INCOME' and amount < 0:
            category = 'MISC'
        elif amount > 0:
            category = 'INCOME'

        transaction = self.model(amount=amount, category=category,
                                 transfer_method=transfer_method, customer_id=customer_id)
        transaction.full_clean()
        transaction.save()
