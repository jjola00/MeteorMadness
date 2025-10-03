from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from api.health import health_bp
from utils.errors import handle_error

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    load_dotenv()

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    app.register_blueprint(health_bp, url_prefix='/api')

    # Register error handlers
    app.register_error_handler(Exception, handle_error)


    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
