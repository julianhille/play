import logging


def delete_track_post_process(db, track_id):
    db.playlists.update(
        {'tracks': {'$in': [track_id]}}, {'$pull': {'tracks': track_id}}, multi=True)


def add_logging(application):
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    application.logger.addHandler(handler)
