from flask import Flask
from config import config
from models.film import Base, engine, SessionLocal


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    from models.film import init_db
    init_db()

    from app_routes import main
    app.register_blueprint(main)

    return app
