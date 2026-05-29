from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import include, path
from pathlib import Path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            'api/docs/',
            TemplateView.as_view(
                template_name='redoc.html'
            ),
        ),
        path(
            'api/openapi-schema.yml',
            serve,
            {
                'document_root': settings.BASE_DIR / 'docs',
                'path': 'openapi-schema.yml',
            },
        ),
    ]
    
    
    static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
