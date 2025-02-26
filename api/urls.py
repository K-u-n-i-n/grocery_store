from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CategoryListView, ProductListView

v1_router = DefaultRouter()
v1_router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('products/', ProductListView.as_view(), name='products-list'),
    path('', include(v1_router.urls)),
]
