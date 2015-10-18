import pymongo


def ensure_indices(db):  # nocov
    # artists
    db.artists.create_index([('name', pymongo.DESCENDING)], background=True)
    db.artists.create_index([('search', pymongo.DESCENDING)], background=True)
    db.artists.create_index([('discogs_id', pymongo.DESCENDING)], background=True)

    # users
    db.users.ensure_index([('name', pymongo.DESCENDING)], unique=True, background=True)

    # tracks
    db.tracks.ensure_index([('search', pymongo.TEXT)], background=True)
    db.tracks.ensure_index([('hash', pymongo.DESCENDING)], background=True)

    # directories
    db.directories.ensure_index([('path', pymongo.ASCENDING)], background=True, unique=True)
    db.directories.ensure_index([('name', pymongo.ASCENDING)], background=True)

    # playlists
    db.playlists.ensure_index([('name', pymongo.TEXT)], background=True)
    db.playlists.ensure_index([('owner', pymongo.ASCENDING)], background=True)
    db.playlists.ensure_index([('public', pymongo.ASCENDING)], background=True)
