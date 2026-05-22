import os

from flask import Flask

from config import APP_NAME, APP_TAGLINE, DATA_DIR, LOGO_DIR, SECRET_KEY
from routes.candidati import candidati_bp
from routes.dettaglio import dettaglio_bp
from routes.display import display_bp
from routes.export import export_bp
from routes.home import home_bp
from routes.logo import logo_bp
from routes.session_manage import manage_bp
from routes.settings import settings_bp
from routes.scrutiny import scrutiny_bp


def create_app():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGO_DIR, exist_ok=True)
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
    app.register_blueprint(home_bp)
    app.register_blueprint(scrutiny_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(logo_bp)
    app.register_blueprint(display_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(candidati_bp)
    app.register_blueprint(manage_bp)
    app.register_blueprint(dettaglio_bp)

    @app.context_processor
    def inject_branding():
        return {"app_name": APP_NAME, "app_tagline": APP_TAGLINE}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
