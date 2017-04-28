from flask import jsonify


def unauthenticated():
    response = jsonify({'error': 'unauthenticated'})
    response.status_code = 401
    return response


def forbidden():
    response = jsonify({'error': 'forbidden'})
    response.status_code = 403
    return response
