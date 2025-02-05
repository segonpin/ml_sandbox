import os

from sklearn.model_selection import train_test_split
import h2o

from h2o.estimators.gbm import H2OGradientBoostingEstimator
from h2o.estimators.xgboost import H2OXGBoostEstimator
from h2o.estimators.random_forest import H2ORandomForestEstimator
from h2o.estimators.deeplearning import H2ODeepLearningEstimator

import pandas as pd
from dataclasses import dataclass

DATA_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data"))

@dataclass
class Dataset:
    name: str
    rel_paths: list[tuple[str]]
    cat_columns: list[str]
    label: str
    predictors: list[str]


DATASETS = {
    "prostate": Dataset(
        name="prostate", 
        rel_paths=[("prostate", "prostate.csv")],
        cat_columns=["CAPSULE"],
        label="CAPSULE",
        predictors=['AGE', 'RACE', 'DPROS', 'DCAPS', 'PSA', 'VOL', 'GLEASON'],
    ),
    "diabetes": Dataset(
        name="diabetes", 
        rel_paths=[("diabetes", "diabetic_data.csv")],
        cat_columns=["CAPSULE"],
        label="CAPSULE",
        predictors=['AGE', 'RACE', 'DPROS', 'DCAPS', 'PSA', 'VOL', 'GLEASON'],
    ),
    "zillow": Dataset(
        name="zillow", 
        rel_paths=[
            ("zillow", "zillow-train.csv"),
            ("zillow", "zillow-train.csv")
        ],
        cat_columns=["CAPSULE"],
        label="CAPSULE",
        predictors=['AGE', 'RACE', 'DPROS', 'DCAPS', 'PSA', 'VOL', 'GLEASON'],
    ),
}

class DataHandler:
    def __init__(self, data_path=DATA_PATH):
        self.data_path = data_path

    def load_dataset_prostate(self):
        """
        from https://docs.h2o.ai/h2o/latest-stable/h2o-py/docs/intro.html
         ID  CAPSULE  AGE  RACE  DPROS  DCAPS   PSA   VOL  GLEASON
0         1        0   65   1.0      2      1   1.4   0.0        6
1         2        0   72   1.0      3      2   6.7   0.0        7
2         3        0   70   1.0      1      2   4.9   0.0        6
...     ...      ...  ...   ...    ...    ...   ...   ...      ...
194557  378        1   76   1.0      2      1   5.5  53.9        8
194558  379        0   69   2.0      2      1   1.5   8.6        5
194559  380        0   69   1.0      2      1   1.9  20.7        6

[194560 rows x 9 columns]"""
        data_file = os.path.join(self.data_path, "prostate", "prostate.csv")
        df = pd.read_csv(data_file)
        self.dtrain, self.dtest = train_test_split(df, test_size=0.10, random_state=42)
        self.dtrain, self.dvalid = train_test_split(self.dtrain, test_size=0.33, random_state=42)

        self.categorical_columns = ["CAPSULE"]
        # self.numerical_columns = ['ID', 'AGE', 'RACE', 'DPROS', 'DCAPS', 'PSA', 'VOL', 'GLEASON']

        self.label = "CAPSULE"
        self.predictors = ['AGE', 'RACE', 'DPROS', 'DCAPS', 'PSA', 'VOL', 'GLEASON']

    def load_dataset_diabetes(self):
        data_file = os.path.join(self.data_path, "dataset_diabetes", "diabetic_data.csv")
        self.data = pd.read_csv(data_file)
        ids_mapping_file = os.path.join(self.data_path, "dataset_diabetes", "IDs_mapping.csv")
        self.ids_mapping = pd.read_csv(ids_mapping_file)

    def load_zillow_housing_prices(self):
        # http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-test.csv
        # http://s3.amazonaws.com/h2o-public-test-data/bigdata/server/timeseries/zillow-housing-prices-train.csv
        train_data_file = os.path.join(self.data_path, "zillow-train.csv")
        self.dtrain = pd.read_csv(train_data_file)
        test_data_file = os.path.join(self.data_path, "zillow-test.csv")
        self.dtest = pd.read_csv(test_data_file)


class H2ORFWrapper():
    def __init__(self):
        h2o.init()

    def load_data(self, data):
        self.dtrain = h2o.H2OFrame(data.dtrain)
        self.dvalid = h2o.H2OFrame(data.dvalid)
        self.dtest = h2o.H2OFrame(data.dtest)

        # cast to factor
        for col in data.categorical_columns:
            self.dtrain[col] = self.dtrain[col].asfactor()
            self.dvalid[col] = self.dvalid[col].asfactor()
            self.dtest[col] = self.dtest[col].asfactor()
        
        self.predictors = data.predictors
        self.label = data.label

    def train(self):
        self.m = H2ORandomForestEstimator(ntrees=200,
            stopping_rounds=2,
            score_each_iteration=True,
            seed=123)
        # m = H2OGradientBoostingEstimator(ntrees=10, max_depth=5)

        # train the model
        self.m.train(x=self.predictors, y=self.label, training_frame=self.dtrain, validation_frame=self.dvalid)
        self.m.score_history()

        # https://docs.h2o.ai/h2o/latest-stable/h2o-docs/data-science/drf.html?highlight=mse
        # show the performance on the validation data
        self.m.model_performance(valid=True)
        # score and compute new metrics on the test data!
        self.m.model_performance(test_data=self.dtest)

    def evaluate(self):
        pred = self.m.predict(self.dtest)["predict"].as_data_frame()
        actual = self.dtest[self.label].as_data_frame()
        # metrics = h2o.make_metrics(pred, actual)
        print((pred["predict"]-actual[self.label]).abs().mean())


def main():
    data_handler = DataHandler()
    data_handler.load_dataset_prostate()

    h2orf = H2ORFWrapper()
    h2orf.load_data(data_handler)
    h2orf.train()
    h2orf.evaluate()

if __name__ == "__main__":
    main()
