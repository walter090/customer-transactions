from rest_framework.serializers import HyperlinkedModelSerializer

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
