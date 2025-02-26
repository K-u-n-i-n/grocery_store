from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from store.models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class CategoryListView(generics.ListAPIView):
    """Эндпоинт для просмотра списка категорий с подкатегориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination


class ProductListView(generics.ListAPIView):
    """Эндпоинт для просмотра списка продуктов."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = PageNumberPagination
