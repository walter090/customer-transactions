import os

from rest_framework.decorators import action
import requests
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import permissions
from .management.permissions import IsSelfOrAdmin

from .management.paginators import CustomerPaginator
from .management.secret_constants import APIConsts
from .models import Customer
from . import serializers
from decimal import Decimal


class CustomerView(ModelViewSet):
    queryset = Customer.objects.all()
    pagination_class = CustomerPaginator
    filter_backends = [OrderingFilter, DjangoFilterBackend, SearchFilter]

    ordering = ['last_name', '-creation_date', ]
    search_fields = ['=username', '=email', ]

    def get_serializer_class(self):
        serializer_assignment = {
            'retrieve': serializers.CustomerRetrievalSerializer,
            'create': serializers.CustomerCreationSerializer
        }

        return serializers.CustomerSerializer if self.action not in serializer_assignment \
            else serializer_assignment[self.action]

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        elif self.action == 'destroy' \
                or self.action == 'update' \
                or self.action == 'partial_update' \
                or self.action == 'retrieve' \
                or self.action == 'verify':
            permission_classes = [IsSelfOrAdmin]
        elif self.action == 'verify':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    # @method_decorator(csrf_protect)
    def create(self, request, *args, **kwargs):
        """ Create new customer."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            try:
                Customer.objects.create(username=data['username'],
                                        email=data['email'],
                                        first_name=data['first_name'],
                                        last_name=data['last_name'],
                                        birth_year=data['birth_year'],
                                        occupation_type=data['occupation_type'],
                                        balance=data['balance'],
                                        password=data['password'])
            except ValidationError as ve:
                return Response({'error': ve}, status=400)

            return Response({'message': 'Customer created.'}, status=200)
        else:
            return Response({'error': serializer.errors}, status=400)

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve information on an individual customer."""
        customer = self.get_object()
        customer_id = customer.identifier

        token = request.META['HTTP_AUTHORIZATION']
        data = {'customer_id': customer_id}
        headers = {'Authorization': token}
        url = os.path.join(APIConsts.TRANSACTION_API_ROOT.value, 'info', '')

        response = requests.post(url=url, data=data, headers=headers)

        if response.status_code != requests.codes.ok:
            return Response(response,
                            status=response.status_code)

        transactions_data = response.json()
        customer_data = self.get_serializer(customer).data
        customer_data['transaction_info'] = transactions_data

        return Response(customer_data)

    @action(methods=['post'], detail=False)
    def transfer(self, request, *args, **kwargs):
        """ Make a transfer and update customer account balance."""
        amount = Decimal(request.data['amount'])
        customer_id = request.data['customer_id']
        customer = self.queryset.get(identifier=customer_id)

        balance = customer.balance + amount
        if balance < 0:
            return Response({'error': 'Account overdrawn.'}, status=400)

        customer.balance = balance
        customer.save()
        return Response({'message': 'Account balance updated.'}, status=200)

    @action(methods=['get'], detail=False)
    def verify(self, request, *args, **kwargs):
        return Response({'message': 'Token verified.'}, status=200)
