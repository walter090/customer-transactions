from rest_framework.serializers import HyperlinkedModelSerializer, Field

from .models import Transaction


class TransactionSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'customer_id',
            'amount',
            'category',
            'transfer_method',
        )


class TransactionUsernameSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'amount',
            'category',
            'transfer_method',
        )


class TransactionRetrievalSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'identifier',
            'customer_id',
            'amount',
            'category',
            'transfer_method',
            'balance_after',
        )
