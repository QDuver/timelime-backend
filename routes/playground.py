
from flask import Blueprint, jsonify, request
from decorators.decorators import error_handler
playground_bp = Blueprint('playground', __name__)
from models.user import User
import config as c

@playground_bp.route("/playground/", endpoint="test", methods=['POST'])
@error_handler
def playground():

    User(uid='0Gu3S71O2Thq0bSv5DTY7pszf1P2')

    return jsonify('coucou'), 200