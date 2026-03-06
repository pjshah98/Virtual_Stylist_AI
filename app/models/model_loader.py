import os
import pickle
from functools import lru_cache


class ModelLoader:
    @lru_cache(maxsize=1)
    def load(self):
        model_path = os.path.join(
            os.path.dirname(__file__),
            "../../ml/models/recommendation_model.pkl",
        )
        model_path = os.path.normpath(model_path)
        with open(model_path, "rb") as f:
            model, feature_names = pickle.load(f)
        return model, feature_names

