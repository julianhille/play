import pymongo


def ensure_indices(db):  # nocov
    # artists
    db.artists.create_index([('name', pymongo.DESCENDING)], background=True)
    db.artists.create_index([('search', pymongo.DESCENDING)], background=True)
    db.artists.create_index([('discogs_id', pymongo.DESCENDING)], background=True)
    db.artists.create_index([('search', pymongo.TEXT)], background=True)

    # users
    db.users.create_index([('name', pymongo.DESCENDING)], unique=True, background=True)

    # tracks
    db.tracks.create_index(
        [('search.artist', pymongo.TEXT),
         ('search.title', pymongo.TEXT),
         ('search.file', pymongo.TEXT)],
        background=True)
    db.tracks.create_index([('hash', pymongo.DESCENDING)], background=True)
    db.tracks.create_index([('path', pymongo.DESCENDING)], background=True, unique=True)

    # directories
    db.directories.create_index([('path', pymongo.ASCENDING)], background=True, unique=True)
    db.directories.create_index([('name', pymongo.ASCENDING)], background=True)

    # playlists
    db.playlists.create_index([('name', pymongo.TEXT)], background=True)
    db.playlists.create_index([('owner', pymongo.ASCENDING)], background=True)
    db.playlists.create_index([('public', pymongo.ASCENDING)], background=True)
