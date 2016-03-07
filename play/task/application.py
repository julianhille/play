import os
import re

from celery import Celery, current_app
from celery.utils.log import get_task_logger
from bson import BSON
from kombu.serialization import register
from mutagen import File

from play.config import config
from play.lock import lock
from play.task.utils import hash_file


def _create_app():
    app = Celery(__name__)
    app.config_from_object(config)
    register('bson', BSON.encode, BSON.decode,
             content_type='application/bson',
             content_encoding='utf-8')
    return app


logger = get_task_logger(__name__)
application = _create_app()
file_ext = ('.mp3')


@application.task
def directory_scan(id_):
    db = current_app.backend.database
    directory = db.directories.find_one({'_id': id_})
    logger.info("Processing:  Directory with id '{}'".format(id_))
    if not directory:
        logger.warn('Directory: {} couldn\'t be found in database'.format(id_))
        return
    with lock(db.directories, id_) as lock_id:
        logger.info('Locking directory {} with lock id {}'.format(id_, lock_id))
        if not os.path.exists(directory['path']):
            db.directories.find_and_modify({'_id': id_}, {'active': False})
            # @TODO(jhille): disable all tracks from this directory / or delete
            logger.warn('Directory: {} couldn\'t be found on filesystem'.format(directory['path']))
            return
        for root, dirs, files in os.walk(directory['path'], followlinks=False):
            for file in files:
                if file.endswith(file_ext):
                    track_path = os.path.join(root, file)
                    insert = {'path': track_path, 'directory': id_}
                    track = db.tracks.find_and_modify(
                        query={'path': track_path}, update=insert, upsert=True, new=True)
                    logger.info('Directory: {} found file {}'.format(id_, track))
                    audio_scan.apply_async(args=[track['_id']], queue='play')


@application.task
def audio_scan(id_):
    db = current_app.backend.database
    logger.info("Processing:  File: '{}'".format(id_))
    track = db.tracks.find_one({'_id': id_})
    if not track:
        logger.warn('Track: {} couldn\'t be found in database'.format(id_))
        return

    with lock(db.tracks, id_) as lock_id:
        logger.info('Locking file {} with lock id {}'.format(id_, lock_id))
        if not os.path.isfile(track['path']):
            logger.warn('File: {} couldn\'t be found'.format(track['path']))
            db.tracks.find_and_modify({'_id': id_}, update={'active': False}, upsert=False)
            return
        if not db.directories.find_one({'_id': track['directory']}):
            db.tracks.find_and_modify({'_id': id_}, update={'active': False}, upsert=False)
            logger.warn('Files: {} parent directory ({}) couldn\'t be found'.format(
                track['_id'], track['directory']))
            return

        file_name = os.path.basename(track['path'])
        size = os.path.getsize(track['path'])
        name = os.path.splitext(file_name)[0]
        search = re.sub('([^0-9a-zA-Z]+)', ' ', name)
        track.update({
            'active': True,
            'name': name,
            'search': {'file': search},
            'size': size,
            'hash': hash_file(track['path'], size),
        })
        add_audio_information(track['path'], track)
        db.tracks.update({'_id': id_}, track)


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
