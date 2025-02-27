from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from store.models import Category, Product, Subcategory

User = get_user_model()


# Фикстуры для тестирования API
@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='pass')


@pytest.fixture
def authenticated_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def product(db):
    # Создаем связанные объекты для продукта
    category = Category.objects.create(name='Test Category', image=None)
    subcategory = Subcategory.objects.create(
        name='Test Subcategory', image=None, category=category)
    return Product.objects.create(
        name='Test Product',
        price=10.0,
        subcategory=subcategory
    )


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestCartAPI:
    CART_URL = '/api/v1/cart/'
    ADD_ITEM_URL = '/api/v1/cart/add/'

    def test_get_cart(self, authenticated_client):
        response = authenticated_client.get(self.CART_URL)
        assert response.status_code == HTTPStatus.OK
        data = response.data
        assert 'items' in data
        assert 'total_items' in data
        assert 'total_sum' in data

    def test_add_item_to_cart(self, authenticated_client, product):
        new_data = {'product_id': product.id, 'quantity': 2}
        # POST-запрос для добавления продукта в корзину
        response = authenticated_client.post(
            self.ADD_ITEM_URL, data=new_data, format='json')
        assert response.status_code == HTTPStatus.CREATED
        # GET-запрос для проверки, что элемент добавлен
        response_get = authenticated_client.get(self.CART_URL)
        assert response_get.status_code == HTTPStatus.OK
        items = response_get.data.get('items')
        assert any(item['product']['id'] == product.id for item in items)


@pytest.mark.django_db
def test_category_list(client):
    # Создаем категорию и подкатегорию (slug генерируется автоматически)
    category = Category.objects.create(name='Test Category', image=None)
    Subcategory.objects.create(
        name='Test Subcategory', image=None, category=category)

    response = client.get('/api/v1/categories/')
    assert response.status_code == 200
    data = response.json()
    # если данные пагинированы, извлекаем результат
    if isinstance(data, dict) and 'results' in data:
        data = data['results']
    # Проверяем, что список не пустой и содержит подкатегории
    assert isinstance(data, list)
    assert any('subcategories' in cat and isinstance(
        cat['subcategories'], list) for cat in data)
