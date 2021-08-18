from server.endpoints.models import Endpoint, MLAlgorithm, MLAlgorithmStatus


class MLRegistry:
    def __init__(self):
        self.endpoints = {}

    def add_algorithm(self, **kwargs):
        endpoint, _ = Endpoint.objects.get_or_create(name=kwargs['endpoint_name'], owner=kwargs['owner'])
        database_object, algorithm_created_at = MLAlgorithm.objects.get_or_create(
            name=kwargs['algorithm_name'],
            description=kwargs['algorithm_description'],
            code=kwargs['algorithm_code'],
            version=kwargs['algorithm_version'],
            owner=['owner'],
            parent_endpoint=kwargs['parent_endpoint'],
        )
        if algorithm_created_at:
            status = MLAlgorithmStatus(
                status=kwargs['algorithm_status'],
                created_by=kwargs['owner'],
                parent_mlalgorithm=database_object,
                is_active=True,
            )
            status.save()

        self.endpoints[database_object.id] = kwargs['algorithm_object']

