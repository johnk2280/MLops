from django.test import TestCase

# from server.ml.real_estate_price_prediction.random_forest import RandomForestModel
from server.ml.real_estate_price_prediction.random_forest import RandomForestModel


class MLTests(TestCase):
    def test_rf_model(self):
        data = {
            "Id": 7202,
            "DistrictId": 94,
            "Rooms": 1.0,
            "Square": 35.81547646722722,
            "LifeSquare": 22.301367212492828,
            "KitchenSquare": 6.0,
            "Floor": 9,
            "HouseFloor": 9.0,
            "HouseYear": 1975,
            "Ecology_1": 0.127375905,
            "Ecology_2": "B",
            "Ecology_3": "B",
            "Social_1": 43,
            "Social_2": 8429,
            "Social_3": 3,
            "Healthcare_1": "",
            "Helthcare_2": 3,
            "Shops_1": 9,
            "Shops_2": "B"
        }

        algorithm_under_test = RandomForestModel()
        response = algorithm_under_test.predict(data)
        self.assertEqual('OK', response['status'])
        self.assertTrue('predicted_price' in response['message'])
