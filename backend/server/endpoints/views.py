import json

from django.db import transaction
from django.shortcuts import render

from rest_framework import viewsets, mixins, views, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from .models import Endpoint, MLAlgorithm, MLAlgorithmStatus, MLRequest
from .serializers import EndpointSerializer, MLAlgorithmSerializer, MLAlgorithmStatusSerializer, MLRequestSerializer
from ml.registry import MLRegistry
from server.wsgi import registry


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
    queryset = MLAlgorithmStatus.objects.all()

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


class PredictView(views.APIView):
    def post(self, request, endpoint_name, format=None):
        algorithm_status = self.request.query_params.get('status', 'production')
        algorithm_version = self.request.query_params.get('version')
        algorithms = MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name,
            status__status=algorithm_status,
            status__is_active=True,
        )

        if algorithm_version:
            algorithms = algorithms.filter(version=algorithm_version)

        if len(algorithms) == 0:
            return Response(
                {"status": "Error", "message": "ML algorithm is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(algorithms) != 1:
            return Response(
                {"status": "Error",
                 "message": "ML algorithm selection is ambiguous. Please specify algorithm version."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        algorithm_object = registry.endpoints[algorithms[0].id]
        prediction = algorithm_object.predict(request.data)

        label = prediction['label'] if 'label' in prediction else 'error'
        ml_request = MLRequest(
            input_data=json.dumps(request.data),
            full_response=prediction,
            response=label,
            feedback='',
            parent_mlalgorithm=algorithms[0],
        )
        ml_request.save()

        prediction['request_id'] = ml_request.id

        return Response(prediction)

