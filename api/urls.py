from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from .views import CartViewSet, CategoryListView, ProductListView

v1_router = DefaultRouter()
v1_router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('categories/', CategoryListView.as_view(), name='categories-list'),
    path('products/', ProductListView.as_view(), name='products-list'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'swagger/', SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
    path('', include(v1_router.urls)),
]
