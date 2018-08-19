import datetime

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from person.util import auxiliary
from .management.managers import CustomerManager


class Customer(AbstractBaseUser, PermissionsMixin):
    OCCUPATION = [
        ('MANAGERIAL', 'Managerial'),
        ('PROFESSIONAL', 'Professional'),
        ('CLERICAL', 'Clerical'),
        ('TECHNICAL', 'Technical'),
        ('SERVICE', 'Service'),
        ('AGRICULTURAL', 'Agricultural'),
        ('ELEMENTARY', 'Elementary'),
        ('MILITARY', 'Military'),
        ('MISC', 'Miscellaneous'),
    ]

    identifier = models.CharField(max_length=20, unique=True,
                                  primary_key=True, default=auxiliary.make_id,
                                  editable=False)
    username = models.CharField(max_length=50, unique=True,
                                null=False, blank=False)
    email = models.EmailField(unique=True, null=False,
                              blank=False)
    password = models.CharField(null=False, blank=False, max_length=100)
    first_name = models.CharField(max_length=30, null=False,
                                  blank=False)
    last_name = models.CharField(max_length=30, null=False,
                                 blank=False)

    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    creation_date = models.DateField(null=False, default=datetime.date.today)
    birth_year = models.IntegerField(null=False, blank=False)
    occupation_type = models.CharField(max_length=20, null=False,
                                       choices=OCCUPATION, default='MISC')

    balance = models.DecimalField(null=False, default=0,
                                  max_digits=32, decimal_places=2)

    objects = CustomerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'birth_year']

    def __str__(self):
        return self.username
