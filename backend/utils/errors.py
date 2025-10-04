from flask import jsonify

def handle_error(e):
    """Generic error handler."""
    response = {
        "error": "Internal Server Error",
        "message": str(e)
    }
    return jsonify(response), 500
