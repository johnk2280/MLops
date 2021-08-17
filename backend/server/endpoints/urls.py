from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from views import EndpointViewSet, MLAlgorithmViewSet, MLAlgorithmStatusViewSet, MLRequestViewSet

# app_name = 'endpoints'

router = DefaultRouter(trailing_slash=False)
router.register('endpoints', EndpointViewSet, basename='endpoints')
router.register('mlalgorithms', MLAlgorithmViewSet, basename='mlalgorithms')
router.register('mlalgorithmstatuses', MLAlgorithmStatusViewSet, basename='mlalgorithmstatuses')
router.register('mlrequests', MLRequestViewSet, basename='mlrequests')

urlpatterns = [
    url(r'^api/v1/', include(router.urls))
]
