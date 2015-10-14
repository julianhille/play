from celery import Celery, current_app
from celery.utils.log import get_task_logger

from datetime import datetime
import os
import re
from scandir import scandir

from .utils import hash_file


def _create_app():
    app = Celery(__name__, config_source='play.default_settings')
    return app


logger = get_task_logger(__name__)
application = _create_app()
file_ext = ('.mp3')


@application.task
def directory_scan(dir_path):
    dir_path = os.path.abspath(dir_path)
    directory = current_app.backend.database.directories.find_one({'path': dir_path})
    logger.info("Processing:  Directory: '{}'".format(directory))
    if not directory:
        logger.warn('Directory: {} couldn\'t be found in database'.format(dir_path))
        return
    if not os.path.exists(dir_path):
        current_app.backend.database.directories.update(
            {'path': dir_path}, {'$set': {'status': False}})
        logger.warn('Directory: {} couldn\'t be found on filesystem'.format(dir_path))
        return
    for item in scandir(directory['path']):
        if item.is_dir():
            insert = {
                'parent': directory['_id'],
                'parents': directory.get('parents', []) + [directory['_id']],
                'name': item.name,
                'path': os.path.abspath(item.path),
                'scanned': datetime.now(),
                'status': True
            }
            current_app.backend.database.directories.update(
                {'path': item.path}, insert, upsert=True)
            directory_scan.delay(item.path)
        elif item.is_file() and item.name.endswith(file_ext):
            scan_audio.delay(item.path)


@application.task
def scan_audio(file_path):
    logger.info("Processing:  File: '{}'".format(file_path))
    if not os.path.isfile(file_path):
        logger.warn('File: {} couldn\'t be found'.format(file_path))
        return
    file_path = os.path.abspath(file_path)
    directory_path = os.path.abspath(os.path.dirname(file_path))
    directory = current_app.backend.database.directories.find_one({'path': directory_path})
    if not directory:
        logger.warn('Files: {} parent directory couldn\'t be found'.format(file_path))
        return
    file_name = os.path.basename(file_path)
    size = os.path.getsize(file_path)
    name = os.path.splitext(file_name)[0]
    search = re.sub('([^0-9a-zA-Z]+)', ' ', name)
    insert = {
        'name': name,
        'search': search,
        'path': file_path,
        'directory': directory['_id'],
        'parent_directories': directory.get('parents', []) + [directory['_id']],
        'size': size,
        'hash': hash_file(file_path, size)
    }
    current_app.backend.database.tracks.update({'path': file_path}, insert, upsert=True)
