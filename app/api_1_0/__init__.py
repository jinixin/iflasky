from flask import Blueprint

api = Blueprint('api', __name__)

from . import user, post, comment, authentication