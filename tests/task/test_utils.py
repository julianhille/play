from pyfakefs.fake_filesystem import FakeFileOpen
from play.task import utils
from unittest.mock import patch


def test_hash(file_system):
    ffo = FakeFileOpen(file_system)
    with patch('play.task.utils.open', ffo, create=True):
        assert (
            utils.hash_file('/tmp/open/git.test', 100) ==
            '72a02b238bf1e8c26ca9bfdaedf0e8bcdb96744b')
        assert (
            utils.hash_file('/tmp/open/git.test', 200) ==
            '435782fe04508db5db668828bcb15b9223785d26')
