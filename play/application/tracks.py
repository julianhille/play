from bson import ObjectId
from flask import abort, current_app, send_file

from play.application.blueprint import Blueprint


SCHEMA = {
    'item_title': 'track',
    'public_item_methods': [],
    'item_methods': ['GET'],
    'resource_methods': ['GET'],
    'allowed_roles': ['user', 'admin'],
    'schema': {
        'artist': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'artists',
                'embeddable': True
            }
        },
        'length': {
            'type': 'integer'
        },
        'metadata': {
            'type': 'dict'
        },
        'name': {
            'type': 'string'
        }
    }
}


blueprint = Blueprint('tracks', __name__, SCHEMA)


@blueprint.route('/stream/<regex("[a-f\d]{24}"):track_id>', methods=["GET"])
def stream(track_id):
    if not current_app.auth.authorized(['user'], 'stream', 'GET'):
        abort(401)

    track = current_app.data.driver.db['tracks'].find_one({'_id': ObjectId(track_id)}, {'file': 1})
    if not track:
        abort(404)

    try:
        with open(track['file'], "rb") as fp:
            return send_file(fp, mimetype='audio/mpeg',
                             attachment_filename=str(track_id))
    except IOError:
        pass
    abort(500)
