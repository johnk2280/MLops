from datetime import datetime
from pathlib import Path
import random
import json

import joblib

import numpy as np
import pandas as pd
import matplotlib

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score as r2
from sklearn.model_selection import KFold, GridSearchCV

import seaborn as sns


class DataPreprocessing:

    def __init__(self):
        self.medians = None
        self.kitchen_square_quantile = None

    def fit(self, incoming_data):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        models_dir = base_dir.joinpath('research')
        self.medians = joblib.load(models_dir.joinpath('medians.joblib'))
        self.kitchen_square_quantile = joblib.load(models_dir.joinpath('kitchen_square_quantile.joblib'))

    def transform(self, incoming_data):
        incoming_data = json.load(incoming_data)
        print(incoming_data, type(incoming_data))
        # Rooms
        incoming_data.loc[incoming_data['Rooms'] >= 6, 'Rooms'] = incoming_data['Rooms'] // 10
        incoming_data.loc[incoming_data['Rooms'] == 0, 'Rooms'] = 1

        # KitchenSquare
        condition = (
                        incoming_data['KitchenSquare'].isna()) | (
                                incoming_data['KitchenSquare'] > self.kitchen_square_quantile
                                ) | (incoming_data['KitchenSquare'] == 0)

        incoming_data.loc[condition, 'KitchenSquare'] = incoming_data['Square'] * .2

        incoming_data.loc[incoming_data['KitchenSquare'] < 3, 'KitchenSquare'] = 3

        # HouseFloor, Floor
        condition_2 = (incoming_data['HouseFloor'] == 0) | (incoming_data['HouseFloor'] > 90)
        incoming_data.loc[condition_2, 'HouseFloor'] = incoming_data['Floor']

        condition_3 = (incoming_data['Floor'] > incoming_data['HouseFloor'])
        incoming_data.loc[condition_3, 'Floor'] = incoming_data['HouseFloor']

        # HouseYear
        current_year = datetime.now().year

        incoming_data['HouseYear_outlier'] = 0
        incoming_data.loc[incoming_data['HouseYear'] > current_year, 'HouseYear_outlier'] = 1

        incoming_data.loc[incoming_data['HouseYear'] > current_year, 'HouseYear'] = current_year

        # Healthcare_1
        if 'Healthcare_1' in incoming_data.columns:
            incoming_data.drop('Healthcare_1', axis=1, inplace=True)

        # LifeSquare
        expression = (incoming_data['Square'] * .9 - incoming_data['KitchenSquare'])
        incoming_data.loc[(incoming_data['LifeSquare'].isna()), 'LifeSquare'] = expression

        condition_3 = (incoming_data['LifeSquare'] > expression)
        incoming_data.loc[condition_3, 'LifeSquare'] = expression

        incoming_data.fillna(self.medians, inplace=True)

        return incoming_data


class FeatureGenerator:
    """Генерация новых фич"""

    def __init__(self):
        self.DistrictId_counts = None
        self.binary_to_numbers = None
        self.med_price_by_district = None
        self.med_price_by_floor_year = None
        self.house_year_max = None
        self.floor_max = None
        self.district_size = None

    def fit(self, incoming_data, y=None):
        incoming_data = incoming_data.copy()

        # Binary features
        self.binary_to_numbers = {'A': 0, 'B': 1}

        # DistrictID
        self.district_size = incoming_data['DistrictId'].value_counts().reset_index() \
            .rename(columns={'index': 'DistrictId', 'DistrictId': 'DistrictSize'})

    def transform(self, incoming_data):
        # Binary features
        incoming_data['Ecology_2'] = incoming_data['Ecology_2'].map(
            self.binary_to_numbers)  # self.binary_to_numbers = {'A': 0, 'B': 1}
        incoming_data['Ecology_3'] = incoming_data['Ecology_3'].map(self.binary_to_numbers)
        incoming_data['Shops_2'] = incoming_data['Shops_2'].map(self.binary_to_numbers)

        # DistrictId, IsDistrictLarge
        incoming_data = incoming_data.merge(self.district_size, on='DistrictId', how='left')

        incoming_data['new_district'] = 0
        incoming_data.loc[incoming_data['DistrictSize'].isna(), 'new_district'] = 1

        incoming_data['DistrictSize'].fillna(5, inplace=True)

        incoming_data['IsDistrictLarge'] = (incoming_data['DistrictSize'] > 100).astype(int)

        return incoming_data

    def floor_to_cat(self, incoming_data):
        bins = [0, 3, 5, 9, 15, self.floor_max]
        incoming_data['floor_cat'] = pd.cut(incoming_data['Floor'], bins=bins, labels=False)

        incoming_data['floor_cat'].fillna(-1, inplace=True)
        return incoming_data

    def year_to_cat(self, incoming_data):
        bins = [0, 1941, 1945, 1980, 2000, 2010, self.house_year_max]
        incoming_data['year_cat'] = pd.cut(incoming_data['HouseYear'], bins=bins, labels=False)

        incoming_data['year_cat'].fillna(-1, inplace=True)
        return incoming_data


class RandomForestModel:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        models_dir = base_dir.joinpath('research')
        self.preprocessor = DataPreprocessing()
        self.features_gen = FeatureGenerator()
        self.model = joblib.load(models_dir.joinpath('rf_model.joblib'))
        # self.preprocessor = joblib.load(models_dir.joinpath('preprocessor.joblibd'))
        # self.features_gen = joblib.load(models_dir.joinpath('features_gen.joblibd'))

    def preprocess_the_data(self, input_data):
        input_data = pd.DataFrame(input_data, index=[0])
        self.preprocessor.fit(input_data)
        input_data = self.preprocessor.transform(input_data)
        return input_data

    def generate_features(self, input_data):
        self.features_gen.fit(input_data)
        input_data = self.features_gen.transform(input_data)
        return input_data

    def predict(self, input_data):
        try:
            input_data = self.generate_features(self.preprocess_the_data(input_data))
            return self.model.predict(input_data)
        except Exception as e:
            return {'status': 'Error', 'message': str(e)}
