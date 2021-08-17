from django.db import transaction
from django.shortcuts import render

from rest_framework import viewsets, mixins
from rest_framework.exceptions import APIException

from models import Endpoint, MLAlgorithm, MLAlgorithmStatus, MLRequest
from serializers import EndpointSerializer, MLAlgorithmSerializer, MLAlgorithmStatusSerializer, MLRequestSerializer


class EndpointViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EndpointSerializer
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(
        parent_mlalgorithm=instance.parent_mlalgorithm,
        created_at__lt=instance.created_at,
        active=True,
    )

    for i in range(len(old_statuses)):
        old_statuses[i].is_active = False

    MLAlgorithmStatus.objects.bulk_update(old_statuses, ['is_active'])


class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
):
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.object.all()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(is_active=True)
                deactivate_other_statuses(instance)
        except Exception as e:
            raise APIException(str(e))


class MLRequestViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
    mixins.UpdateModelMixin,
):
    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()


