import csv
import datetime
import json
import logging
import os
from collections import defaultdict
from decimal import Decimal

import requests
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from requests.exceptions import HTTPError
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .management.paginators import TransactionPaginator
from .management.secret_constants import APIConsts
from .models import Transaction
from .serializers import TransactionSerializer, TransactionRetrievalSerializer

logger = logging.getLogger(__name__)


class TransactionView(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPaginator
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    ordering = ['-transfer_time']
    search_fields = ['=category', '=transfer_method']

    def get_serializer_class(self):
        if self.action == 'destroy' or \
                self.action == 'retrieve' or \
                self.action == 'list':
            return TransactionRetrievalSerializer
        else:
            return TransactionSerializer

    @staticmethod
    def _get_last_month(rewind_months=None, to_date=False):
        """ Get datetime object of the first and last days of last months"""
        if rewind_months is None:
            rewind_months = 1

        if rewind_months == 0:
            to_date = True

        today = datetime.date.today()
        day = today - relativedelta(months=rewind_months)

        last_month_first = datetime.date(day.year, day.month, 1)
        last_month_last = today + relativedelta(days=1) if to_date else \
            datetime.date(today.year, today.month, 1) - relativedelta(days=1)

        return last_month_first, last_month_last

    def list(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')

        url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, 'verify_admin', '')
        headers = {'Authorization': token}
        response = requests.get(url, headers=headers)

        if response.status_code != requests.codes.ok:
            return Response(response, status=response.status_code)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """ Create a transaction.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            customer_id = data['customer_id']
            amount = data['amount']

            token = request.META.get('HTTP_AUTHORIZATION')

            try:
                Transaction.objects.create(customer_id=customer_id,
                                           amount=amount,
                                           category=data['category'],
                                           transfer_method=data['transfer_method'],
                                           token=token)
            except HTTPError as he:
                logger.warning(he)
                return Response({'error': he})
            except ValidationError as ve:
                logger.warning(ve)
                return Response({'error': ve}, status=400)

            return Response({'message': 'Transaction made.'}, status=200)
        else:
            return Response({'error': serializer.errors}, status=400)

    @action(methods=['post'], detail=False)
    def info(self, request, *args, **kwargs):
        """ Get transaction history for customer.
        """
        customer_id = request.data['customer_id']
        if not APIConsts.TESTING.value:
            token = request.META.get('HTTP_AUTHORIZATION')

            url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, customer_id, 'verify', '')
            headers = {'Authorization': token}
            response = requests.get(url=url, headers=headers)

            if response.status_code != requests.codes.ok:
                return Response({'error': response}, status=response.status_code)

        last_month_first, last = self._get_last_month(to_date=True)

        # All transactions by this customer since last month.
        queryset = self.get_queryset().filter(Q(customer_id=customer_id)
                                              & Q(transfer_time__range=[last_month_first,
                                                                        last]))

        if not queryset:
            return Response({
                'message': 'Customer has not made any transactions last month.'},
                status=200)

        last_month_trans = []
        total_spending = Decimal('0')
        total_income = Decimal('0')
        methods = defaultdict(Decimal)
        spending = defaultdict(Decimal)

        for transaction in queryset:
            last_month_trans.append({
                'identifier': transaction.identifier,
                'customer_id': transaction.customer_id,
                'amount': transaction.amount,
                'category': transaction.category,
                'transfer_method': transaction.transfer_method,
                'transfer_time': transaction.transfer_time,
                'balance_after': transaction.balance_after,
            })

            if transaction.amount < 0:
                total_spending -= transaction.amount
                methods[transaction.transfer_method] -= transaction.amount
                spending[transaction.category] -= transaction.amount
            else:
                total_income += transaction.amount

        methods_ratio = {key: str(round(methods[key] / total_spending, 2)) for key in methods}
        spending_ratio = {key: str(round(spending[key] / total_spending, 2)) for key in spending}

        methods = {key: str(methods[key]) for key in methods}
        spending = {key: str(spending[key]) for key in spending}

        transaction_info = {
            'total_spending': total_spending,
            'total_income': total_income,
            'transfer_methods': json.dumps(methods),
            'transfer_methods_ratio': json.dumps(methods_ratio),
            'spending': json.dumps(spending),
            'spending_ratio': json.dumps(spending_ratio),
            'last_month_history': last_month_trans,
        }

        return Response(transaction_info)

    @action(methods=['get'], detail=False)
    def dataset(self, request, *args, **kwargs):
        rewind = request.query_params.get('rewind')
        token = request.META.get('HTTP_AUTHORIZATION')

        try:
            rewind = int(rewind)
        except ValueError:
            rewind = None
        except TypeError:
            rewind = None

        start, end = self._get_last_month(rewind_months=rewind, to_date=True)
        queryset = self.get_queryset() \
            .filter(transfer_time__range=[start, end]) \
            .order_by('transfer_time')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="dataset.csv"'
        writer = csv.writer(response)
        writer.writerow(['occupation', 'birth_year', 'transfer_method', 'category', 'balance'])

        for transaction in queryset:
            customer_id = transaction.customer_id

            url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, customer_id, 'basic', '')
            headers = {'Authorization': token}
            customer_response = requests.get(url, headers=headers)

            if customer_response.status_code != requests.codes.ok:
                return Response({'error': 'Not authorized'}, status=405)
            else:
                customer = customer_response.json()

            writer.writerow([customer['occupation_type'], customer['birth_year'],
                             transaction.transfer_method, transaction.category,
                             transaction.balance_after + transaction.amount])

        return response

    def destroy(self, request, *args, **kwargs):
        """ DELETE action not allowed on transactions.
        """
        logger.warning('Request to delete transaction {} received,'
                       ' DELETE is not allowed on transactions.'.format(self.get_object().identifier))
        return Response({'error': 'Delete action not allowed on transactions'}, status=400)

    def partial_update(self, request, *args, **kwargs):
        """ PATCH not allowed on transactions.
        """
        logger.warning('Request to update transaction {} received,'
                       ' PATCH is not allowed on transactions.'.format(self.get_object().identifier))
        return Response({'error': 'PATCH action not allowed on transactions'}, status=400)

    def update(self, request, *args, **kwargs):
        """ PUT not allowed on transactions.
        """
        logger.warning('Request to update transaction {} received,'
                       ' PUT is not allowed on transactions.'.format(self.get_object().identifier))
        return Response({'error': 'PUT action not allowed on transactions'}, status=400)
