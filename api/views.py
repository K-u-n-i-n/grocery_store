from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from store.models import Cart, CartItem, Category, Product

from .serializers import (
    CartItemActionSerializer,
    CartSerializer,
    CategorySerializer,
    ProductSerializer,
)


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


class CartViewSet(viewsets.ViewSet):
    """
    ViewSet для работы с корзиной.
    Доступен только авторизованным пользователям.
    """

    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        """
        Получить или создать корзину для текущего пользователя.
        """
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        """
        GET /api/cart/
        Выводит содержимое корзины с подсчетом общего количества товаров
        и суммы.
        """
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add')
    def add_item(self, request):
        """
        POST /api/cart/add/
        Добавляет продукт в корзину. Если продукт уже есть,
        увеличивает количество.
        Ожидает: {"product_id": <id>, "quantity": <int>}
        """
        serializer = CartItemActionSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'detail': 'Продукт не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
            cart = self.get_cart(request)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            return Response(
                {'detail': 'Продукт добавлен в корзину'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], url_path='update')
    def update_item(self, request):
        """
        PUT /api/cart/update/
        Обновляет количество продукта в корзине.
        Ожидает: {"product_id": <id>, "quantity": <int>}
        """
        serializer = CartItemActionSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity = serializer.validated_data['quantity']
            cart = self.get_cart(request)
            try:
                cart_item = cart.items.get(product_id=product_id)
            except CartItem.DoesNotExist:
                return Response(
                    {'detail': 'Элемент корзины не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
            cart_item.quantity = quantity
            cart_item.save()
            return Response(
                {'detail': 'Количество обновлено'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], url_path='remove')
    def remove_item(self, request):
        """
        DELETE /api/cart/remove/
        Удаляет продукт из корзины.
        Ожидает: {"product_id": <id>}
        """
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'detail': 'product_id обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart = self.get_cart(request)
        try:
            cart_item = cart.items.get(product_id=product_id)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Элемент корзины не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """
        DELETE /api/cart/clear/
        Полностью очищает корзину.
        """
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
