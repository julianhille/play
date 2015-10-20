from bson import ObjectId
from bson.errors import InvalidId
from eve.auth import requires_auth
from flask.ext.login import current_user
from flask import abort, current_app, request

from play.api.blueprint import Blueprint
from play.api.application import send_file_partial
from play.task.application import scan_audio
from play.utils import delete_track_post_process

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


blueprint = Blueprint('tracks', __name__, SCHEMA, url_prefix='/tracks')


@blueprint.hook('on_pre_GET')
def ensure_only_active(request, lookup):
    if not current_user.is_authenticated or not current_user.has_role(['admin']):
        lookup['active'] = True


@blueprint.route('/stream/<regex("[a-f\d]{24}"):track_id>', methods=["GET"])
def stream(track_id):
    if not current_user.is_authenticated:
        abort(401)
    lookup = {'_id': ObjectId(track_id)}
    if not current_user.has_role(['admin']):
        lookup['active'] = True
    track = current_app.data.driver.db['tracks'].find_one(lookup, {'path': 1, 'hash': 1})
    print(track)
    if not track:
        abort(404)

    try:
        return send_file_partial(track['path'], track['hash'])
    except:
        pass
    abort(500)


@blueprint.route('/rescan', methods=['PUT'])
@requires_auth('me')
def trigger_rescan():
    if not current_user.has_role(['admin']):
        abort(401)
    body = request.get_json()

    try:
        id_ = ObjectId(body.get('_id'))
    except InvalidId:
        abort(422, 'invalid _id')

    track = current_app.data.driver.db['tracks'].find_one({'_id': id_}, {'path': 1})
    if not track:
        abort(404)
    scan_audio.delay(track['path'])
    return '', 204


@blueprint.hook('on_deleted_item')
def ensure_delete_from_playlists(original):
    delete_track_post_process(current_app.data.driver.db, original['_id'])
