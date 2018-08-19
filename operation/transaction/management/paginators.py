from rest_framework.pagination import CursorPagination


class TransactionPaginator(CursorPagination):
    ordering = '-transfer_time'
    page_size = 10
