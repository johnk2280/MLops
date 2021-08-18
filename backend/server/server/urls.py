from django.contrib import admin
from django.urls import path, include

# from backend.server.endpoints.urls import urlpatterns as endpoints_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('endpoints.urls'))
    # endpoints_urlpatterns,
]

