from django.urls import path
from .views import *

urlpatterns = [
    path('list/', products, name='product_lists'),
    path('<int:product_id>/', product_details, name = 'product_details'),
    path('cart/', cart_lists, name='cart_lists'),
    path('cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', delete_from_cart, name='delete_from_cart'),
    path('order/', create_order, name='create_order'),
    path('order/lists/', order_lists, name='order_lists'),


]
