# urls.py
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from . import views
import os
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalog, name='catalog'),
    path('product-detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('application/', views.order_application, name='application_page'),
]

# Принудительное добавление обработчиков
media_root = settings.MEDIA_ROOT
static_root = settings.STATIC_ROOT

print(f"Adding media route for: {media_root}")
print(f"Adding static route for: {static_root}")

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': str(media_root)}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': str(static_root)}),
]