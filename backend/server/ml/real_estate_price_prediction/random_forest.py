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
    """Подготовка исходных данных"""

    def __init__(self):
        """Параметры класса"""
        self.medians = None
        self.kitchen_square_quantile = None

    def fit(self, X):
        """Сохранение статистик"""
        # Расчет медиан
        self.medians = X.median()
        # self.kitchen_square_quantile = X['KitchenSquare'].quantile(.975)

    def transform(self, X):
        """Трансформация данных"""

        # Rooms
        X.loc[X['Rooms'] >= 6, 'Rooms'] = X['Rooms'] // 10
        X.loc[X['Rooms'] == 0, 'Rooms'] = 1

        # KitchenSquare
        condition = (
                        X['KitchenSquare'].isna()) | (X['KitchenSquare'] > self.kitchen_square_quantile
                                                      ) | (X['KitchenSquare'] == 0)

        X.loc[condition, 'KitchenSquare'] = X['Square'] * .2

        X.loc[X['KitchenSquare'] < 3, 'KitchenSquare'] = 3

        # HouseFloor, Floor
        condition_2 = (X['HouseFloor'] == 0) | (X['HouseFloor'] > 90)
        X.loc[condition_2, 'HouseFloor'] = X['Floor']

        condition_3 = (X['Floor'] > X['HouseFloor'])
        X.loc[condition_3, 'Floor'] = X['HouseFloor']

        # HouseYear
        current_year = datetime.now().year

        X['HouseYear_outlier'] = 0
        X.loc[X['HouseYear'] > current_year, 'HouseYear_outlier'] = 1

        X.loc[X['HouseYear'] > current_year, 'HouseYear'] = current_year

        # Healthcare_1
        if 'Healthcare_1' in X.columns:
            X.drop('Healthcare_1', axis=1, inplace=True)

        # LifeSquare
        expression = (X['Square'] * .9 - X['KitchenSquare'])
        X.loc[(X['LifeSquare'].isna()), 'LifeSquare'] = expression

        condition_3 = (X['LifeSquare'] > expression)
        X.loc[condition_3, 'LifeSquare'] = expression

        X.fillna(self.medians, inplace=True)

        return X


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

    def fit(self, X, y=None):
        X = X.copy()

        # Binary features
        self.binary_to_numbers = {'A': 0, 'B': 1}

        # DistrictID
        self.district_size = X['DistrictId'].value_counts().reset_index() \
            .rename(columns={'index': 'DistrictId', 'DistrictId': 'DistrictSize'})

    def transform(self, X):
        # Binary features
        X['Ecology_2'] = X['Ecology_2'].map(self.binary_to_numbers)  # self.binary_to_numbers = {'A': 0, 'B': 1}
        X['Ecology_3'] = X['Ecology_3'].map(self.binary_to_numbers)
        X['Shops_2'] = X['Shops_2'].map(self.binary_to_numbers)

        # DistrictId, IsDistrictLarge
        X = X.merge(self.district_size, on='DistrictId', how='left')

        X['new_district'] = 0
        X.loc[X['DistrictSize'].isna(), 'new_district'] = 1

        X['DistrictSize'].fillna(5, inplace=True)

        X['IsDistrictLarge'] = (X['DistrictSize'] > 100).astype(int)

        return X

    def floor_to_cat(self, X):
        bins = [0, 3, 5, 9, 15, self.floor_max]
        X['floor_cat'] = pd.cut(X['Floor'], bins=bins, labels=False)

        X['floor_cat'].fillna(-1, inplace=True)
        return X

    def year_to_cat(self, X):
        bins = [0, 1941, 1945, 1980, 2000, 2010, self.house_year_max]
        X['year_cat'] = pd.cut(X['HouseYear'], bins=bins, labels=False)

        X['year_cat'].fillna(-1, inplace=True)
        return X


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
