from RAI.metrics.metric_group import MetricGroup
import math
import numpy as np
import scipy.stats

# Move config to external .json? 
_config = {
    "name": "stat_moment_group",
    "compatibility": {"type_restriction": None, "output_restriction": None},
    "dependency_list": [],
    "tags": ["stats", "Moments"],
    "complexity_class": "linear",
    "metrics": {
        "moment-1": {
            "display_name": "First Moment",
            "type": "vector",
            "has_range": False,
            "range": None,
            "explanation": "Mean is the expected value of data.",
        },
        "moment-2": {
            "display_name": "Second Moment",
            "type": "vector",
            "has_range": False,
            "range": None,
            "explanation": "Mean is the expected value of data.",
        },
        "moment-3": {
            "display_name": "Third Moment",
            "type": "vector",
            "has_range": False,
            "range": None,
            "explanation": "Mean is the expected value of data.",
        },
    }
}

# Type (Regression, Classification, Data | probability, numeric)


class StatMomentGroup(MetricGroup, config=_config):
    compatibility = {"type_restriction": None, "output_restriction": None}

    def __init__(self, ai_system) -> None:
        super().__init__(ai_system)
        
    def update(self, data):
        pass

    def compute(self, data_dict):
        if "data" in data_dict:
            args = {}
            if self.ai_system.user_config is not None and "stats" in self.ai_system.user_config and "args" in self.ai_system.user_config["stats"]:
                args = self.ai_system.user_config["stats"]["args"]
            data = data_dict["data"]

            scalar_data = data.X[:,self.ai_system.meta_database.scalar_mask]

            self.metrics["moment-1"].value = scipy.stats.moment(scalar_data, 1)
            self.metrics["moment-2"].value = scipy.stats.moment(scalar_data, 2)
            self.metrics["moment-3"].value = scipy.stats.moment(scalar_data, 3)

 