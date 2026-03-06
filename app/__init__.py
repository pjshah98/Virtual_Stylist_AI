from flask import Flask

from .config import get_config


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Blueprints
    from .routes.main_routes import main_bp
    from .routes.api_routes import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
