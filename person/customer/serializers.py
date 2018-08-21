from rest_framework.serializers import HyperlinkedModelSerializer

from .models import Customer


class CustomerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'identifier',
            'username',
            'email',
            'first_name',
            'last_name',
            'birth_year',
            'occupation_type',
        )


class CustomerCreationSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
            'birth_year',
            'occupation_type',
        )


class CustomerRetrievalSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'identifier',
            'username',
            'email',
            'first_name',
            'last_name',
            'creation_date',
            'birth_year',
            'occupation_type',
            'balance',
        )
