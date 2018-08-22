# Customer Transactions Microservices

## Introduction
Rest APIs for customer and transaction microservices implemented using
Django Rest Framework.

## Requirements
Python 3.6

Install packages from requirements.txt

Create `.env` file base on `.env.template`, keep information in `.env` file secret.
By default, static files are sent to an aws s3 instance, you can change to another service and change
`.env` and `settings.py`.

## Authentication and authorization
All users and interactions between services need to be authenticated. Requests made to the APIs
should attach OAuth2 authorization in their header.

To enable OAuth2, create a superuser and log into the admin console and create an OAuth application.

### Create a superuser
Go to `person` folder and create superuser by typing
```commandline
python manage.py createsuperuser
```
Superuser/staff status grants you full access to the data.
