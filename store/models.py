import os
from io import BytesIO

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from PIL import Image


class CustomUser(AbstractUser):
    '''Модель пользователя, наследуемая от AbstractUser.'''

    def __str__(self):
        return self.username


class Category(models.Model):
    '''Модель категории товаров.'''

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Subcategory(models.Model):
    '''Модель подкатегории товаров, привязанная к категории.'''

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='subcategories/')

    class Meta:
        verbose_name = 'подкатегория'
        verbose_name_plural = 'Подкатегории'
        default_related_name = 'subcategories'

    def __str__(self):
        return f'{self.category.name} - {self.name}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    '''Модель продукта с изображениями в 3-х размерах.'''

    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_original = models.ImageField(
        upload_to='products/original/'
    )
    image_medium = models.ImageField(
        upload_to='products/medium/',
        blank=True, null=True
    )
    image_thumbnail = models.ImageField(
        upload_to='products/thumbnail/',
        blank=True, null=True
    )

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'Продукты'
        default_related_name = 'products'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''
        Переопределенный метод сохранения для авто-генерации изображений
        среднего размера и миниатюры.
        '''
        super().save(*args, **kwargs)
        if self.image_original and (
            not self.image_medium or not self.image_thumbnail
        ):
            img = Image.open(self.image_original.path)
            medium_size = (500, 500)
            thumb_size = (100, 100)

            # Создание среднего изображения
            img_medium = img.copy()
            img_medium.thumbnail(medium_size)
            temp_medium = BytesIO()
            img_medium.save(temp_medium, format=img.format)
            temp_medium.seek(0)
            medium_name = os.path.basename(self.image_original.name)
            self.image_medium.save(medium_name, ContentFile(
                temp_medium.read()), save=False)

            # Создание миниатюры
            img_thumb = img.copy()
            img_thumb.thumbnail(thumb_size)
            temp_thumb = BytesIO()
            img_thumb.save(temp_thumb, format=img.format)
            temp_thumb.seek(0)
            thumb_name = os.path.basename(self.image_original.name)
            self.image_thumbnail.save(
                thumb_name, ContentFile(temp_thumb.read()), save=False)

            super().save(update_fields=['image_medium', 'image_thumbnail'])


class Cart(models.Model):
    '''Модель корзины, привязанная к пользователю.'''

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'Корзины'
        default_related_name = 'cart'

    def __str__(self):
        return f'Корзина пользователя {self.user}'

    def total_sum(self):
        """Возвращает общую стоимость корзины."""
        return sum(item.get_total() for item in self.items.all())


class CartItem(models.Model):
    """Модель элемента корзины."""

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'store.Product', on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'элемент корзины'
        verbose_name_plural = 'Элементы корзины'
        default_related_name = 'items'

    def __str__(self):
        return f'{self.product.name} x {self.quantity}'

    def get_total(self):
        """Возвращает общую стоимость элемента корзины."""
        return self.product.price * self.quantity
