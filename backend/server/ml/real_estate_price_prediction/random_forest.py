from datetime import datetime
from pathlib import Path

import joblib

import pandas as pd


class DataPreprocessing:
    def __init__(self):
        self.medians: dict = {}
        self.kitchen_square_quantile: float = 0
        self.base_dir = Path(__file__).resolve().parent.parent.parent.parent
        self.models_dir = self.base_dir.joinpath('research')

    def fit(self):
        self.medians = joblib.load(self.models_dir.joinpath('medians.joblib'))
        self.kitchen_square_quantile = joblib.load(self.models_dir.joinpath('kitchen_square_quantile.joblib'))

    def transform(self, incoming_data: pd.DataFrame) -> pd.DataFrame:
        # Rooms
        incoming_data.loc[incoming_data['Rooms'] >= 6, 'Rooms'] = incoming_data['Rooms'] // 10
        incoming_data.loc[incoming_data['Rooms'] == 0, 'Rooms'] = 1

        # KitchenSquare
        kitchen_square_condition = (
                                       incoming_data['KitchenSquare'].isna()) | (
                                           incoming_data['KitchenSquare'] > self.kitchen_square_quantile
                                   ) | (incoming_data['KitchenSquare'] == 0)

        incoming_data.loc[kitchen_square_condition, 'KitchenSquare'] = incoming_data['Square'] * .2
        incoming_data.loc[incoming_data['KitchenSquare'] < 3, 'KitchenSquare'] = 3

        # HouseFloor, Floor
        house_floor_condition = (incoming_data['HouseFloor'] == 0) | (incoming_data['HouseFloor'] > 90)
        incoming_data.loc[house_floor_condition, 'HouseFloor'] = incoming_data['Floor']

        floor_condition = (incoming_data['Floor'] > incoming_data['HouseFloor'])
        incoming_data.loc[floor_condition, 'Floor'] = incoming_data['HouseFloor']

        # HouseYear
        current_year = datetime.now().year
        incoming_data['HouseYear_outlier'] = 0
        incoming_data.loc[incoming_data['HouseYear'] > current_year, 'HouseYear_outlier'] = 1
        incoming_data.loc[incoming_data['HouseYear'] > current_year, 'HouseYear'] = current_year

        # Healthcare_1
        if 'Healthcare_1' in incoming_data.columns:
            incoming_data.drop('Healthcare_1', axis=1, inplace=True)

        # LifeSquare
        life_square_expression = (incoming_data['Square'] * .9 - incoming_data['KitchenSquare'])
        incoming_data.loc[(incoming_data['LifeSquare'].isna()), 'LifeSquare'] = life_square_expression

        life_square_condition = (incoming_data['LifeSquare'] > life_square_expression)
        incoming_data.loc[life_square_condition, 'LifeSquare'] = life_square_expression

        incoming_data.fillna(self.medians, inplace=True)

        return incoming_data


class FeatureGenerator:
    """?????????????????? ?????????? ??????"""

    def __init__(self):
        self.DistrictId_counts = None
        self.binary_to_numbers = None
        self.med_price_by_district = None
        self.med_price_by_floor_year = None
        self.house_year_max = None
        self.floor_max = None
        self.district_size = None

    def fit(self, incoming_data: pd.DataFrame, y=None):
        incoming_data = incoming_data.copy()

        # Binary features
        self.binary_to_numbers = {'A': 0, 'B': 1}

        # DistrictID
        self.district_size = incoming_data['DistrictId'].value_counts().reset_index().rename(
            columns={
                'index': 'DistrictId',
                'DistrictId': 'DistrictSize'
            }
        )

    def transform(self, incoming_data: pd.DataFrame) -> pd.DataFrame:
        # Binary features
        incoming_data['Ecology_2'] = incoming_data['Ecology_2'].map(self.binary_to_numbers)
        incoming_data['Ecology_3'] = incoming_data['Ecology_3'].map(self.binary_to_numbers)
        incoming_data['Shops_2'] = incoming_data['Shops_2'].map(self.binary_to_numbers)

        # DistrictId, IsDistrictLarge
        incoming_data = incoming_data.merge(self.district_size, on='DistrictId', how='left')
        incoming_data['new_district'] = 0
        incoming_data.loc[incoming_data['DistrictSize'].isna(), 'new_district'] = 1
        incoming_data['DistrictSize'].fillna(5, inplace=True)
        incoming_data['IsDistrictLarge'] = (incoming_data['DistrictSize'] > 100).astype(int)

        return incoming_data


class RandomForestModel:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        models_dir = base_dir.joinpath('research')
        self.preprocessor = DataPreprocessing()
        self.features_gen = FeatureGenerator()
        self.model = joblib.load(models_dir.joinpath('rf_model.joblib'))

    def preprocess_the_data(self, input_data: pd.DataFrame) -> pd.DataFrame:
        self.preprocessor.fit()
        input_data = self.preprocessor.transform(input_data)
        return input_data

    def generate_features(self, input_data: pd.DataFrame) -> pd.DataFrame:
        self.features_gen.fit(input_data)
        input_data = self.features_gen.transform(input_data)
        return input_data

    def predict(self, input_data: dict) -> dict:
        input_data = pd.DataFrame(input_data, index=[0])
        try:
            input_data = self.generate_features(self.preprocess_the_data(input_data))
            predicted_price = self.model.predict(input_data)[0]
            return {
                'status': 'OK',
                'price': predicted_price,
                'message': f'predicted_price - {predicted_price}',
            }
        except Exception as e:
            return {
                'status': 'Error',
                'message': str(e)
            }
