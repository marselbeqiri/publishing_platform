from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

api_patterns = [
    path('auth/', include('applications.authentication.urls'), name="authentication"),
    path('publishing/', include('applications.publishing.urls'), name="publishing"),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    from project.swagger_urls import swagger_urlpatterns

    urlpatterns += swagger_urlpatterns

admin.site.site_header = "Publishing Platform 2022"
admin.site.site_title = "Publishing Platform Super Admin Panel"
admin.site.index_title = "Publishing Platform administration area"
