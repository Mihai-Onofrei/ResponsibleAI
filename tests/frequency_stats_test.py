from RAI.dataset import Feature, Data, MetaDatabase, Dataset
from RAI.AISystem import AISystem, Model
import numpy as np

from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
x, y = load_breast_cancer(return_X_y=True)
xTrain, xTest, yTrain, yTest = train_test_split(x, y)

val_0_count = 20

nums = np.ones((xTrain.shape[0], 1))
nums[:val_0_count] = 0
xTrain = np.hstack((xTrain, nums))
xTrain = np.hstack((xTrain, nums))

nums = np.ones((xTest.shape[0], 1))
nums[:val_0_count] = 0
xTest = np.hstack((xTest, nums))
xTest = np.hstack((xTest, nums))

# Set up features
features_raw = ["id", "radius_mean", "texture_mean", "perimeter_mean", "area_mean", "smoothness_mean", "compactness_mean", "concavity_mean", "concave points_mean", "symmetry_mean",
                "fractal_dimension_mean", "radius_se", "texture_se", "compactness_se", "concavity_se",
                "concave points_se", "symmetry_se", "fractal_dimension_se", "radius_worst", "texture_worst", "texture_worst", "perimeter_worst", "area_worst",
                "smoothness_worst", "compactness_worst", "concavity_worst", "concave points_worst", "symmetry_worst", "fractal_dimension_worst", "diagnosis"]
features = []

for feature in features_raw:
    features.append(Feature(feature, "float32", feature))
features.append(Feature("race", "integer", "race value", categorical=True, values={0:"black", 1:"white"}))
features.append(Feature("gender", "integer", "race value", categorical=True, values={1:"male", 0:"female"}))

# Hook data in with our Representation
training_data = Data(xTrain, yTrain)  # Accepts Data and GT
test_data = Data(xTest, yTest)
dataset = Dataset({"train": training_data, "test": test_data})  # Accepts Training, Test and Validation Set
meta = MetaDatabase(features)

# Create a model to make predictions
from sklearn.ensemble import RandomForestClassifier
rfc = RandomForestClassifier(n_estimators=10, criterion='entropy', random_state=0)
model = Model(agent=rfc, task='binary_classification', description="Detect Cancer in patients using skin measurements",
              name="cisco_cancer_ai", display_name="Cisco Health AI", model_class="Random Forest Classifier")

# Create AISystem from previous objects. AISystems are what users will primarily interact with.
configuration = {"fairness": {"priv_group": {"race": {"privileged": 1, "unprivileged": 0}},
                              "protected_attributes": ["race"], "positive_label": 1}}
ai = AISystem("cancer_detection", meta_database=meta, dataset=dataset, model=model)
ai.initialize(user_config=configuration)

# Train model
rfc.fit(xTrain, yTrain)
predictions = rfc.predict(xTest)

# Make Predictions
ai.compute(predictions, data_type='test', tag="binary classification")

metrics = ai.get_metric_values()
info = ai.get_metric_info()

# frequency_stats relfreq {'race': {'black': 0.4965034965034965, 'white': 0.5034965034965035}, 'gender': {'female': 0.4965034965034965, 'male': 0.5034965034965035}}
# frequency_stats cumfreq {'race': {'black': 71.0, 'white': 143.0}, 'gender': {'female': 71.0, 'male': 143.0}}


def test_relfreq():
    """Tests that the RAI relfreq calculation is correct."""
    assert metrics['frequency_stats']['relfreq']['race']['black'] == val_0_count / xTest.shape[0]
    assert metrics['frequency_stats']['relfreq']['race']['white'] == 1 - val_0_count / xTest.shape[0]
    assert metrics['frequency_stats']['relfreq']['gender']['female'] == val_0_count / xTest.shape[0]
    assert metrics['frequency_stats']['relfreq']['gender']['male'] == 1 - val_0_count / xTest.shape[0]


def test_cumfreq():
    """Tests that the RAI cumfreq calculation is correct."""
    assert metrics['frequency_stats']['cumfreq']['race']['black'] == val_0_count
    assert metrics['frequency_stats']['cumfreq']['race']['white'] == xTest.shape[0]
    assert metrics['frequency_stats']['cumfreq']['gender']['female'] == val_0_count
    assert metrics['frequency_stats']['cumfreq']['gender']['male'] == xTest.shape[0]

# TODO: Clarify data assumption that categorical features must start with 0 and increase by 1.
