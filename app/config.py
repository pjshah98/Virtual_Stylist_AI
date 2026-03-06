import os


class BaseConfig:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JSON_SORT_KEYS = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SECRET_KEY = BaseConfig.SECRET_KEY or "dev-secret-key-change-me"


class ProductionConfig(BaseConfig):
    DEBUG = False


def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    if env in {"prod", "production"}:
        return ProductionConfig
    return DevelopmentConfig

