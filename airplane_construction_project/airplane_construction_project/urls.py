from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Airplane Configuration API",
        default_version='v1',
        description="API для заказа на постройку самолёта",
    ),
    url='http://127.0.0.1:8000',  # ← ДОБАВИТЬ ЭТУ СТРОКУ
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bmstu_lab.urls')),
    
    # Swagger UI
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]