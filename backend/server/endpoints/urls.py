from django.conf.urls import url, include
from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import EndpointViewSet, MLAlgorithmViewSet, MLAlgorithmStatusViewSet, MLRequestViewSet

# app_name = 'endpoints'

router = DefaultRouter(trailing_slash=False)
router.register(r'endpoints', EndpointViewSet, basename='endpoints')
router.register(r'mlalgorithms', MLAlgorithmViewSet, basename='mlalgorithms')
router.register(r'mlalgorithmstatuses', MLAlgorithmStatusViewSet, basename='mlalgorithmstatuses')
router.register(r'mlrequests', MLRequestViewSet, basename='mlrequests')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    # path('api/v1/', include('rest_framework.urls', namespace='rest_framework'))
]
