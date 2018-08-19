import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError


class CustomerManager(BaseUserManager):
    def create(self, username, email, first_name,
               last_name, birth_year, password,
               balance=None, occupation_type=None, **kwargs):
        """ Create a new customer

        Args:
            balance: float, Initial deposit of account.
            username: str, Customer account user name.
            email: str, Customer email address.
            first_name: str, Customer first name.
            last_name: str, Customer last name.
            birth_year: int, Year of birth.
            occupation_type: str, Type of occupation.
            password: str, User password.

        Returns:
            None
        """
        kwargs.setdefault('is_superuser', False)

        customer = self.model(**kwargs)

        customer.username = username
        customer.email = email

        # Format first and last names.
        customer.first_name = first_name.strip().lower().capitalize()
        customer.last_name = last_name.strip().lower().capitalize()

        # Check if names have alphabetical letters only.
        if not (customer.last_name.isalpha() and customer.first_name.isalpha()):
            raise ValidationError('Special characters found in names.')

        if birth_year > datetime.date.today().year or datetime.date.today().year - birth_year > 150:
            raise ValidationError('Invalid year of birth.')
        customer.birth_year = birth_year

        customer.occupation_type = occupation_type if occupation_type is not None else 'MISC'
        customer.balance = balance if balance else 0
        customer.set_password(raw_password=password)

        customer.full_clean()
        customer.save()

    def create_superuser(self, username, email, first_name,
                         last_name, birth_year, password,
                         balance=None, occupation_type=None, **kwargs):
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_staff', True)

        if kwargs.get('is_superuser') is not True:
            raise ValueError('The user is not a superuser')

        self.create(username=username, email=email, first_name=first_name,
                    last_name=last_name, birth_year=birth_year, occupation_type=occupation_type,
                    password=password, balance=balance, **kwargs)
