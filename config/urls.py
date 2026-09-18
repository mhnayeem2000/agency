"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

from .pwa import manifest_view, service_worker_view

handler400 = "config.error_views.error_400"
handler403 = "config.error_views.error_403"
handler404 = "config.error_views.error_404"
handler500 = "config.error_views.error_500"

urlpatterns = [
    path('manifest.json', manifest_view, name='manifest'),
    path('service-worker.js', service_worker_view, name='service_worker'),
    path('admin/', admin.site.urls),
    path("",include("accounts.urls")),
    path("students/",include("students.urls")),
]

urlpatterns += [
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {"document_root": settings.STATIC_ROOT},
    ),
]
