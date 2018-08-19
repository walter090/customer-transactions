import os

import requests
from django.core.exceptions import ValidationError
from django.db.models import Manager

from .secret_constants import APIConsts


class TransactionManager(Manager):
    def create(self, customer_id, amount,
               category, transfer_method, token=None):
        """ Create a new transaction, checks if the customer_id exists
        before saving to db.

        Args:
            customer_id: str, Customer identifier, pk.
            amount:
            category:
            transfer_method:
            token:

        Returns:
            None
        """
        if amount == 0:
            raise ValidationError

        url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, 'transfer', '')
        data = {'amount': amount, 'customer_id': customer_id}

        headers = {'Authorization': token} if token else {}

        response = requests.post(url=url, data=data, headers=headers)
        if response.status_code != requests.codes.ok:
            response.raise_for_status()
            return

        transaction = self.model(amount=amount, category=category,
                                 transfer_method=transfer_method, customer_id=customer_id)
        transaction.full_clean()
        transaction.save()
