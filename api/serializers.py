from rest_framework import serializers

from store.models import Cart, CartItem, Category, Product, Subcategory


class SubcategorySerializer(serializers.ModelSerializer):
    """Сериализатор для подкатегорий."""

    class Meta:
        model = Subcategory
        fields = ('id', 'name', 'slug', 'image')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    subcategories = SubcategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image', 'subcategories')


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товаров."""

    category = serializers.CharField(
        source='subcategory.category.name', read_only=True)
    subcategory = serializers.CharField(
        source='subcategory.name', read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'price',
                  'category', 'subcategory', 'images')

    def get_images(self, obj):
        """Возвращает ссылки на изображения."""
        return {
            'original': (
                obj.image_original.url if obj.image_original else None
            ),
            'medium': (
                obj.image_medium.url if obj.image_medium else None
            ),
            'thumbnail': (
                obj.image_thumbnail.url if obj.image_thumbnail else None
            ),
        }


class CartItemActionSerializer(serializers.Serializer):
    """
    Сериализатор для добавления или изменения элемента корзины.
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CartItem.
    Отображает продукт и количество в корзине.
    """

    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ['product', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Cart.
    Отображает состав корзины, общее количество товаров и общую стоимость.
    """

    items = CartItemSerializer(many=True)
    total_items = serializers.SerializerMethodField()
    total_sum = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['items', 'total_items', 'total_sum']

    def get_total_items(self, obj):
        """
        Возвращает общее количество товаров в корзине.
        """
        return sum(item.quantity for item in obj.items.all())

    def get_total_sum(self, obj):
        """
        Возвращает общую стоимость корзины.
        """
        return obj.total_sum()
