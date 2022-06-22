import pandas as pd
import scipy.stats
from RAI.dataset import Feature, Data, MetaDatabase, Dataset
from RAI.AISystem import AISystem, Model
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split


x, y = fetch_california_housing(return_X_y=True)
xTrain, xTest, yTrain, yTest = train_test_split(x, y)

use_dashboard = False
np.random.seed(21)

# Hook data in with our Representation
dataset = Dataset({"train": Data(xTrain, yTrain), "test": Data(xTest, yTest)})

# Indicate the features of the dataset (Columns)
features = [
    Feature("MedInc", 'float32', "Median Income"),
    Feature("HouseAge", 'float32', "Median House age in Block Group"),
    Feature("AveRooms", 'float32', "Average number of rooms per household"),
    Feature("AveBedrms", 'float32', "Average number of bedrooms per household"),
    Feature("Population", 'float32', "Block group population"),
    Feature("AveOccup", 'float32', "Average Number of Household members"),
    Feature("Latitude", 'float32', "Block group Latitude"),
    Feature("Longitude", 'float32', "Block group Longitude")
]
meta = MetaDatabase(features)

# Create a model to make predictions
from sklearn.ensemble import RandomForestRegressor
reg = RandomForestRegressor(n_estimators=15, max_depth=20)
model = Model(agent=reg, task='regression', name="Cisco_RealEstate_AI", model_class="Random Forest Regressor")

# Create AISystem from previous objects. AISystems are what users will primarily interact with.
configuration = {"equal_treatment": {"priv_groups": [("Gender", 1)]}}
ai = AISystem("Regression example", meta_database=meta, dataset=dataset, model=model, enable_certificates=False)
ai.initialize(user_config=configuration)

# Train model
reg.fit(xTrain, yTrain)
predictions = reg.predict(xTest)

# Make Predictions
ai.compute(predictions, data_type='test', tag="regression")

metrics = ai.get_metric_values()
info = ai.get_metric_info()

for g in metrics:
    for m in metrics[g]:
        if "type" in info[g][m]:
            if info[g][m]["type"] in ("numeric", "vector-dict", "text"):
                print(g, m, metrics[g][m])


# TODO: Set up another set of tests with data that has a category in it
def test_dataset_equality():
    """Tests that the old and new datasets match exactly."""
    assert (xTest == ai.dataset.test_data.X).all()
    assert (yTest == ai.dataset.test_data.y).all()
    assert (xTrain == ai.dataset.train_data.X).all()
    assert (yTrain == ai.dataset.train_data.y).all()


# TODO: remove caps from metric name
def test_num_nan_rows():
    """Tests that the RAI num nan rows calculation is correct."""
    xTestDf = pd.DataFrame(xTest, columns=features)
    assert metrics['summary_stats']['num-Nan-rows'] == xTestDf.shape[0] - xTestDf.dropna().shape[0]


# TODO: remove capitals
def test_percent_Nan_rows():
    """Tests that the RAI percent nan rows calculation is correct."""
    xTestDf = pd.DataFrame(xTest, columns=features)
    assert metrics['summary_stats']['percent-Nan-rows'] == (xTestDf.shape[0] - xTestDf.copy().dropna().shape[0])/len(xTestDf)


# TODO: replace all of these names with underscores rather than dash
# TODO: Is this applicable across multiple columns, or should it be ran per column?
def test_kstat_1():
    """Tests that the RAI kstat-1 calculation is correct."""
    assert metrics['summary_stats']['kstat-1'] == scipy.stats.kstat(xTest, 1)


def test_kstat_2():
    """Tests that the RAI kstat-2 calculation is correct."""
    assert metrics['summary_stats']['kstat-2'] == scipy.stats.kstat(xTest, 2)


def test_kstat_3():
    """Tests that the RAI kstat-3 calculation is correct."""
    assert metrics['summary_stats']['kstat-3'] == scipy.stats.kstat(xTest, 3)


def test_kstat_4():
    """Tests that the RAI kstat-1 calculation is correct."""
    assert metrics['summary_stats']['kstat-4'] == scipy.stats.kstat(xTest, 4)


def test_kstatvar():
    """Tests that the RAI kstatvar calculation is correct."""
    assert metrics['summary_stats']['kstatvar'] == scipy.stats.kstatvar(xTest)


def test_iqr():
    """Tests that the RAI kstatvar calculation is correct."""
    assert metrics['summary_stats']['iqr'] == scipy.stats.iqr(xTest)


# TODO: Is this applicable across multiple columns, or should it be ran per column?
def test_bayes_mvs():
    """Tests that the RAI kstatvar calculation is correct."""
    mean, var, std = scipy.stats.bayes_mvs(xTest)
    assert metrics['summary_stats']['bayes-mean-avg'] == mean[0]
    assert metrics['summary_stats']['bayes-var-avg'] == var[0]
    assert metrics['summary_stats']['bayes-std-avg'] == std[0]


# TODO: Is this applicable across multiple columns, or should it be ran per column?
# TODO: Consistency: chance variance to var, or var globally to variance
def test_frozen_mvs():
    """Tests that the RAI kstatvar calculation is correct."""
    mean, var, std = scipy.stats.mvsdist(xTest)
    assert metrics['summary_stats']['frozen-mean-mean'] == mean.mean()
    assert metrics['summary_stats']['frozen-mean-var'] == mean.var()
    assert metrics['summary_stats']['frozen-mean-std'] == mean.std()

    assert metrics['summary_stats']['frozen-variance-mean'] == var.mean()
    assert metrics['summary_stats']['frozen-variance-var'] == var.var()
    assert metrics['summary_stats']['frozen-variance-std'] == var.std()

    assert metrics['summary_stats']['frozen-std-mean'] == std.mean()
    assert metrics['summary_stats']['frozen-std-var'] == std.var()
    assert metrics['summary_stats']['frozen-std-std'] == std.std()

# TODO: Most of these statistic metrics only make when looking at just one variable. Rework.
