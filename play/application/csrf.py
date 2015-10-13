from eve.render import render_json
from flask import Blueprint, Response
from flask.ext.wtf.csrf import generate_csrf


blueprint = Blueprint('csrf', __name__, url_prefix='/csrf')


@blueprint.route('', methods=['GET'])
def csrf():
    csrf = generate_csrf()
    response = Response(render_json({'csrf': csrf}), mimetype='application/json')
    response.set_cookie('XSRF-TOKEN', csrf)
    return response