from rest_framework import serializers

from store.models import Category, Product, Subcategory


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
