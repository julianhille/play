from datetime import datetime
import os
import re

from celery import Celery, current_app
from celery.utils.log import get_task_logger
from mutagen import File
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
        # @TODO(jhille): We should add a "clean up track" task here.
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
        'search': {'file': search},
        'path': file_path,
        'directory': directory['_id'],
        'parent_directories': directory.get('parents', []) + [directory['_id']],
        'size': size,
        'hash': hash_file(file_path, size),
    }
    add_audio_information(file_path, insert)
    current_app.backend.database.tracks.update({'path': file_path}, insert, upsert=True)


def add_audio_information(path, data):
    audio = File(path, easy=True)

    searchable_fields = ['artist', 'title']
    meta_fields = ['artist', 'date', 'genre', 'title']

    meta_data_original = dict(audio.tags)

    data.update({
        'meta_original': meta_data_original,
        'length': audio.info.length,
        'lossless': False,
        'sample_rate': audio.info.sample_rate,
        'bitrate': audio.info.bitrate,
        'track_gain': audio.info.track_gain,
        'track_peak': audio.info.track_peak,
        'type': 'MP3',

    })

    for key in meta_fields:
        if key in meta_data_original:
            data[key] = meta_data_original[key][0]
        else:
            data[key] = ''

    data.setdefault('search', {}).update(
        {k: data[k] for k in searchable_fields
         if k in data})
