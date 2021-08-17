from django.contrib import admin
from django.urls import path


from server.endpoints.urls import urlpatterns as endpoints_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    endpoints_urlpatterns,
]

# urlpatterns += endpoints_urlpatterns
