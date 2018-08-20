import datetime
import logging
import os
from collections import defaultdict
from decimal import Decimal

import requests
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from requests.exceptions import HTTPError
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .management.paginators import TransactionPaginator
from .management.secret_constants import APIConsts
from .models import Transaction
from .serializers import TransactionSerializer

logger = logging.getLogger(__name__)


class TransactionView(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPaginator
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]

    ordering = ['-transfer_time']
    search_fields = ['=category', '=transfer_method']

    def create(self, request, *args, **kwargs):
        """ Create a transaction.
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            data = serializer.data
            customer_id = data['customer_id']
            amount = data['amount']

            if not APIConsts.TESTING.value:
                token = '' if 'HTTP_AUTHORIZATION' not in request.META else request.META['HTTP_AUTHORIZATION']
            else:
                token = None

            try:
                Transaction.objects.create(customer_id=customer_id,
                                           amount=amount,
                                           category=data['category'],
                                           transfer_method=data['transfer_method'],
                                           token=token)
            except HTTPError as he:
                logger.warning(he)
                return Response({'error': str(he)}, he.response.status_code)
            except ValidationError as ve:
                logger.warning(ve)
                return Response({'error': ve}, status=400)

            return Response({'message': 'Transaction made.'}, status=200)
        else:
            return Response({'error': serializer.errors}, status=400)

    def destroy(self, request, *args, **kwargs):
        """ DELETE action not allowed on transactions."""
        return Response({'error': 'Delete action not allowed on transactions'}, status=400)

    @action(methods=['post'], detail=False)
    def info(self, request, *args, **kwargs):
        customer_id = request.data['customer_id']
        if not APIConsts.TESTING.value:
            token = '' if 'HTTP_AUTHORIZATION' not in request.META else request.META['HTTP_AUTHORIZATION']

            url = os.path.join(APIConsts.CUSTOMER_API_ROOT.value, customer_id, 'verify', '')
            headers = {'Authorization': token}
            response = requests.get(url=url, headers=headers)

            if response.status_code != requests.codes.ok:
                return Response({'error': response}, status=response.status_code)

        today = datetime.date.today()
        day = today - relativedelta(months=1)
        # Fist day of last month.
        last_month_first = datetime.date(day.year, day.month, 1)
        # Last day of last month.
        last_month_last = datetime.date(today.year, today.month, 1) - relativedelta(days=1)

        # All transactions by this customer in last month.
        queryset = self.get_queryset().filter(Q(customer_id=customer_id)
                                              | Q(transfer_time__range=[last_month_first,
                                                                        last_month_last]))

        if not queryset:
            return Response({
                'message': 'Customer has not made any transactions last month.'},
                status=200)

        last_month_trans = []
        for transaction in queryset:
            last_month_trans.append({
                'identifier': transaction.identifier,
                'customer_id': transaction.customer_id,
                'amount': transaction.amount,
                'category': transaction.category,
                'method': transaction.transfer_method,
                'time': transaction.transfer_time
            })

        total_spending = Decimal('0')
        total_income = Decimal('0')
        methods = defaultdict(Decimal)
        spending = defaultdict(Decimal)

        for transaction in queryset:
            if transaction.amount < 0:
                total_spending -= transaction.amount
                methods[transaction.transfer_method] += transaction.amount
                spending[transaction.category] += transaction.amount
            else:
                total_income += transaction.amount

        methods_ratio = {key: methods[key] / total_spending for key in methods}
        spending_ratio = {key: spending[key] / total_spending for key in spending}

        transaction_info = {
            'total_spending': total_spending,
            'total_income': total_income,
            'transfer_methods': methods,
            'transfer_methods_ratio': methods_ratio,
            'spending': spending,
            'spending_ratio': spending_ratio,
            'last_month_history': last_month_trans,
        }

        return Response(transaction_info)
