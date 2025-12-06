from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import product_list 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', product_list, name='home'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('products/all/', product_list, name='all_products'),
    path('barter/', include('barter.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
