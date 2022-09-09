from rest_framework.pagination import PageNumberPagination as ParentPageNumberPagination


class PageNumberPagination(ParentPageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100
