from rest_framework.pagination import CursorPagination


class CustomerPaginator(CursorPagination):
    ordering = 'last_name'
    page_size = 10
