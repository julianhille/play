from bson import ObjectId
from flask import abort, current_app, send_file
from flask.ext.login import current_user

from play.application.blueprint import Blueprint


SCHEMA = {
    'item_title': 'track',
    'public_item_methods': [],
    'item_methods': ['GET', 'PATCH', 'PUT'],
    'resource_methods': ['GET'],
    'allowed_item_read_roles': ['user', 'admin'],
    'allowed_item_write_roles': ['admin'],
    'allowed_write_roles': [],
    'allowed_read_roles': ['admin', 'user'],
    'schema': {
        'artist': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'artists',
                'embeddable': True
            }
        },
        'length': {
            'type': 'integer',
            'readonly': True
        },
        'metadata': {
            'type': 'dict'
        },
        'name': {
            'type': 'string'
        },
        'directory': {
            'type': 'objectid',
            'readonly': True
        },
        'parent_directories': {
            'type': 'list',
            'schema': {
                'type': 'objectid'
            },
            'readonly': True
        },
        'active': {
            'type': 'boolean',
            'roles': ['admin']
        }
    }
}


blueprint = Blueprint('tracks', __name__, SCHEMA)


@blueprint.hook('on_pre_GET')
def ensure_only_active(request, lookup):
    if not current_user.is_authenticated or not current_user.has_role(['admin']):
        lookup['active'] = True


@blueprint.route('/stream/<regex("[a-f\d]{24}"):track_id>', methods=["GET"])
def stream(track_id):
    if not current_user.is_authenticated:
        abort(401)
    lookup = {'_id': ObjectId(track_id)}
    if 'admin' not in current_user.roles:
        lookup['active'] = True
    track = current_app.data.driver.db['tracks'].find_one(lookup, {'file': 1})
    if not track:
        abort(404)

    try:
        with open(track['file'], "rb") as fp:
            return send_file(fp, mimetype='audio/mpeg',
                             attachment_filename=str(track_id))
    except IOError:
        pass
    abort(500)
