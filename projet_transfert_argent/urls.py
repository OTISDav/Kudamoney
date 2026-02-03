from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Configuration du schema
schema_view = get_schema_view(
    openapi.Info(
        title="KudaMoney API",
        default_version='v1',
        description="Documentation API pour KudaMoney",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
        #route admin
    path("admin/", admin.site.urls),

         #routes api
    path('api/users/', include('users.urls')),
    path('api/wallets/', include('wallets.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/support/', include('support.urls')),

                  # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0),
                    name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

                  # Redoc UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
