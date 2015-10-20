

def delete_track_post_process(db, track_id):
    db.playlist.update(
        {'tracks': {'$in': [track_id]}}, {'$pull': {'tracks': track_id}})
