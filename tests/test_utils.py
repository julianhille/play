from play import utils
from bson import ObjectId


def test_post_process_deletion(mongodb):
    track = ObjectId('adf19b92e21e1560a7dd0000')
    assert any(track in p['tracks'] for p in mongodb.playlists.find())
    utils.delete_track_post_process(mongodb, track)
    assert all(track not in p['tracks'] for p in mongodb.playlists.find())
