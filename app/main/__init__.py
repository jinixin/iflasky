from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
from ..errors import *
from ..models import Permit


@main.app_context_processor
def inject_permit():
    return dict(Permit=Permit)
