from flask import Blueprint


auth = Blueprint('auth', __name__)
# print('auth blueprint __name__ = {}'.format(__name__))

from . import views

