"""
URL configuration for ofspace project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        security_definitions = super().get_security_definitions()
        # Override Token security to ensure proper format
        if 'Token' in security_definitions:
            security_definitions['Token'] = {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Token-based authentication. IMPORTANT: Enter "Token <your_token>" (include the word "Token" followed by a space, then your token). Example: Token 8c1cd3cdd19469d77c84086dfc42a21ca2a118b1'
            }
        return security_definitions

schema_view = get_schema_view(
   openapi.Info(
      title="OFSPACE API",
      default_version='v1',
      description="API documentation for OFSPACE.CO backend. Use the login endpoint to get your authentication token, then click the 'Authorize' button above. IMPORTANT: Enter 'Token <your_token>' (include the word 'Token' followed by a space, then your token). Example: Token 8c1cd3cdd19469d77c84086dfc42a21ca2a118b1",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@ofspace.co"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   generator_class=CustomOpenAPISchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/settings/', include('settings.urls')),
    
    # Swagger/OpenAPI documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
