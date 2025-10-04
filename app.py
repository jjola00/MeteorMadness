from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

from backend.api.health import health_bp
from backend.api.asteroids import asteroids_bp
from utils.errors import handle_error
from config import config, setup_logging, get_logger, RequestLoggingMiddleware

# Load environment variables
load_dotenv()

# Setup logging
setup_logging(config)
logger = get_logger(__name__)

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # Configure Flask from config class
    app.config.from_object(config)
    
    # Set Flask-specific configurations
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    app.config['TESTING'] = config.TESTING
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    
    logger.info(f"Starting Flask app in {config.FLASK_ENV} mode")

    # Enable CORS with configuration
    CORS(app, resources={
        f"{config.API_PREFIX}/*": {
            "origins": config.CORS_ORIGINS
        }
    })
    
    # Add request logging middleware
    if config.LOG_LEVEL == 'DEBUG':
        app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app, config)

    # Register Blueprints
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(asteroids_bp, url_prefix='/api')

    # Register error handlers
    app.register_error_handler(Exception, handle_error)
    logger.info("Registered error handlers")

    logger.info("Flask application created successfully")
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    
    logger.info(f"Starting server on port {port}")
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=config.DEBUG
    )
