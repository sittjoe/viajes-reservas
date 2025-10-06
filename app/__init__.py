"""Flask application factory for the travel itinerary generator."""

from flask import Flask


def create_app() -> Flask:
    """Create the Flask application and register routes."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-this-secret"  # pragma: allowlist secret

    from .main import main_bp

    app.register_blueprint(main_bp)

    return app
