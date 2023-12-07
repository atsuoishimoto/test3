from django.contrib import admin
from django.urls import path

from healthcheck import views as healthcheck_views

urlpatterns = [
    path("_/admin/", admin.site.urls),
    path("healthcheck", healthcheck_views.healthcheck),
]
