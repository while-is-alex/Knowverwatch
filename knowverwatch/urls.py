from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = ([
    path('admin/', admin.site.urls),
    path('', include('stats.urls')),
])
# to server static files with Django, add the next line inside the parenthesis
# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT))
