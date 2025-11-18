from django.contrib import admin
from django.urls import path, include
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("engine.urls")),
    path('api/', include('engine.urls_api')),      # 纯 REST
    path('ws/', include('engine.routing')),        # WebSocket
]