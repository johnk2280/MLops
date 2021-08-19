"""
WSGI config for server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import inspect

from django.core.wsgi import get_wsgi_application

from ml.registry import MLRegistry
from ml.real_estate_price_prediction import random_forest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = get_wsgi_application()

try:
    registry = MLRegistry()
    rf_model = random_forest.RandomForestModel()
    registry.add_algorithm(
        endpoint_name='real_estate_price_prediction',
        algorithm_object='rf_model',
        algorithm_name='random forest',
        algorithm_status='production',
        algorithm_version='0.0.1',
        owner='johnk2280',
        algorithm_description='GeekBrains course project for Data Science',
        algorithm_code=inspect.getsource(random_forest)
    )
except Exception as e:
    print("Exception while loading the algorithms to the registry,", str(e), e.__repr__())
