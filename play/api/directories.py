from bson import ObjectId
from bson.errors import InvalidId
from eve.auth import requires_auth
from flask import request, abort
from flask.ext.login import current_app, current_user
from os import path
from play.api.blueprint import Blueprint
from play.task.application import directory_scan

SCHEMA = {
    'item_title': 'directory',
    'public_item_methods': [],
    'item_methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
    'resource_methods': ['GET', 'POST'],
    'allowed_read_roles': ['user', 'admin'],
    'allowed_write_roles': ['admin'],
    'allowed_item_read_roles': ['user', 'admin'],
    'allowed_item_write_roles': ['admin'],
    'schema': {
        'path': {
            'type': 'string',
            'required': True,
            'roles': ['admin'],
            'path': True
        },
        'name': {
            'type': 'string',
            'required': True
        },
        'scanned': {
            'type': 'datetime',
            'roles': ['admin']
        },
    }
}


blueprint = Blueprint('directories', __name__, SCHEMA, url_prefix='/directories')


@blueprint.hook('on_inserted')
def ensure_scan_on_insert(documents):
    for document in documents:
        directory_scan.apply_async(
            args=[document['_id']], queue='play.directory.{}'.format(document['_id']))


@blueprint.hook('on_insert')
@blueprint.hook('on_replace')
@blueprint.hook('on_update')
def ensure_abspath(documents, original=None):
    if not isinstance(documents, list):
        documents = [documents]
    for document in documents:
        if 'path' in document:
            # @TODO (jhille): we need to update all tracks if the path changes
            document['path'] = path.abspath(document['path'])


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

    directory = current_app.data.driver.db['directories'].find_one({'_id': id_}, {'_id': 1})
    if not directory:
        abort(404)
    directory_scan.apply_async(args=[id_], queue='play.directory.{}'.format(id_))
    return '', 204
