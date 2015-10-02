from celery import Celery
from celery.utils.log import get_task_logger

from datetime import datetime
from os import path

from scandir import scandir

from .utils import hash_file


def _create_app():
    app = Celery(__name__, config_source='play.default_settings')
    return app


logger = get_task_logger(__name__)
application = _create_app()
file_ext = ('mp3')


@application.task
def directory_scan(path):
    directory = application.backend.database.directories.find_one({'path': path})
    logger.info("Processing:  Directory: '{}'".format(directory))
    for item in scandir(directory['path']):
        if item.is_dir():
            insert = {
                'parent': directory['_id'],
                'name': item.name,
                'path': item.path,
                'scanned': datetime.now()
            }
            application.backend.database.directories.update(
                {'path': item.path}, insert, upsert=True)
            directory_scan.delay(item.path)
        elif item.is_file() and item.name.endswith(file_ext):
            audio_scan.delay(item.path)


@application.task
def audio_scan(file_path):
    logger.info("Processing:  File: '{}'".format(file_path))
    if not path.isfile(file_path):
        logger.warn('File: {} couldn\'t be found'.format(file_path))
        return
    file_path = path.abspath(file_path)
    directory_path = path.abspath(path.dirname(file_path))
    directory = application.backend.database.directories.find_one({'path': directory_path})
    file_name = path.basename(file_path)
    size = path.getsize(file_path)
    insert = {
        'name': path.splitext(file_name)[0],
        'path': file_path,
        'directory': directory['_id'],
        'size': size,
        'hash': hash_file(file_path, size)
    }
    application.backend.database.tracks.update({'path': file_path}, insert, upsert=True)
    logger.warn('File: {} couldn\'t be found'.format(file_path))
