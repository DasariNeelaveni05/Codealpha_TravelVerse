from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('social.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Django handles STATIC_URL automatically if 'django.contrib.staticfiles' is in INSTALLED_APPS,
    # but if you have custom STATICFILES_DIRS that aren't being picked up:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
