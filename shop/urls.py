from django.urls import path, include
from shop.views import home, post_view,product_detail_view, product_list_view

app_name = 'shop'

urlpatterns = [
    path('', home),
    path('post/', post_view),
    path('product_detail_view/', product_detail_view),
    path('product/<int:id>', product_detail_view, name='product_detail'),
    path('products', product_list_view, name='products')
]