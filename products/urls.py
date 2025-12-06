from django.urls import path
from . import views
from .views import product_list
from .views import product_detail


urlpatterns = [
    path('add/', views.add_product, name='add_product'),
    path('all/', views.all_products, name='all_products'),
    path('my/', views.my_products, name='my_products'),
    path('products/<int:product_id>/', product_detail, name='product_detail'),
    path('toggle_favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('products/toggle_favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('delete/<int:id>/', views.delete_product, name='delete_product'),

]
