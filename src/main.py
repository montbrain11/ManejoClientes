import os
import traceback
import logging
import time

from flask import Flask, jsonify

from src.models.client import db
from src.blueprints.services import services_bp
from src.errors.errors import ApiError # fix was put the complte path previpous was errors.errors

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

def create_app(config_name, local=False):
    app = Flask(__name__)
    app.register_blueprint(services_bp, url_prefix='/clients')

    db_uri = 'sqlite:///clients.db'
    try:
        if not local:
            db_host = os.environ.get('DB_HOST')
            db_port = os.environ.get('DB_PORT')
            db_name = os.environ.get('DB_NAME')
            db_user = os.environ.get('DB_USER')
            db_password = os.environ.get('DB_PASSWORD')

            if all([db_port, db_host, db_name, db_user, db_password]):
                db_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    except Exception as e:
        print(f'Error connecting to db: {e}')
    finally:
        print(db_uri)

    app_context = app.app_context()
    app_context.push()

    db.init_app(app)
    time.sleep(5)
    db.drop_all()
    time.sleep(5)
    db.create_all()
    
    @app.errorhandler(ApiError)
    def handle_exception(err):
        trace = traceback.format_exc()
        logger.info("Log error: " + str(trace))
        return jsonify({"message": err.description}), err.code
    
    return app

app = create_app('manejo-clientes')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)