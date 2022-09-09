from django.conf import settings
from django.contrib import admin
from django.urls import path, include

api_patterns = [
]

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    from project.swagger_urls import swagger_urlpatterns

    urlpatterns += swagger_urlpatterns

admin.site.site_header = "Publishing Platform 2022"
admin.site.site_title = "Publishing Platform Super Admin Panel"
admin.site.index_title = "Publishing Platform administration area"
