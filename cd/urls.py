from django.urls import path
from .views import ProductsListAPIView, SellProductAPIView, ProductsRegisterAPIView, ProductChangeAPIView, BuyProductAPIView, ProductRequestAPIView

urlpatterns = [
    path('info/', ProductsListAPIView.as_view(), name='product_list'),
    path('info/<slug:slug>/', ProductsListAPIView.as_view(), name='product_detail'),
    path('product/sell/<slug:name>/<int:quantity>/', SellProductAPIView.as_view(), name='product_sell'),
    path('product/register/', ProductsRegisterAPIView.as_view(), name='product_register'),
    path('product/change/<slug:slug>/', ProductChangeAPIView.as_view(), name='product_change'),
    path('product/buy/<slug:product>/<int:quantity>/', BuyProductAPIView.as_view(), name='product_buy'),
    path('product/request/', ProductRequestAPIView.as_view(), name='product_request')
]