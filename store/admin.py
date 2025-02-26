from django.contrib import admin

from .models import Cart, CartItem, Category, CustomUser, Product, Subcategory

admin.site.empty_value_display = 'Не задано'


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Класс администрирования пользователей."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'password'
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


class SluggedAdmin(admin.ModelAdmin):
    """Класс администрирования моделей с полем slug."""

    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(SluggedAdmin):
    """Класс администрирования категорий."""

    list_display = ('name', 'slug')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Subcategory)
class SubcategoryAdmin(SluggedAdmin):
    """Класс администрирования подкатегорий."""

    list_display = ('name', 'category', 'slug')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Product)
class ProductAdmin(SluggedAdmin):
    """Класс администрирования товаров."""

    list_display = ('name', 'subcategory', 'price', 'slug')
    list_filter = ('subcategory',)
    search_fields = ('name',)
    ordering = ('name',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('product', 'quantity', 'get_total')
    readonly_fields = ('get_total',)

    @admin.display(description='Общая стоимость')
    def get_total(self, obj):
        return obj.get_total()


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Класс администрирования корзины."""

    list_display = ('user', 'updated_at', 'total_sum')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Класс администрирования элемент корзины."""

    list_display = ('cart', 'product', 'quantity', 'get_total')
    list_filter = ('product', 'cart__user')
    search_fields = ('product__name', 'cart__user__username')
