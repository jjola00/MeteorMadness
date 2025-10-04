from flask import jsonify


class ValidationError(Exception):
    """Custom exception for input validation errors."""
    pass


def handle_error(e):
    """Generic error handler."""
    response = {
        "error": "Internal Server Error",
        "message": str(e)
    }
    return jsonify(response), 500
