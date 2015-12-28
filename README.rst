Play
====
.. image:: https://travis-ci.org/julianhille/play.svg
    :target: https://travis-ci.org/julianhille/play

Play is an open source restful music player.
It uses:
Eve, Flask, Celery, Cerberus, AngularJS

The codebase is thoroughly tested under Python 3.4.


Prerequestions / Dependencies
==============

 - Mongo DB 3.2


Installation
============

pip install git+https://github.com/julianhille/play

export PLAY_CONFIGURATION='/path/to/your/config/file'


Config file
===========

Mandatory:

- MONGO_URI (default: mongodb://localhost:27017/play)
This value is a mongodb connection string including the database.
https://docs.mongodb.org/v3.0/reference/connection-string/

Good to set:

- SECRET_KEY (Flask Session secret, just a long string of random chars)
- WTF_SECRET_KEY (CSRF Secret Key, just a long string of random chars)

Both these are randomized and stored locally on first startup.
This is done bceause otherwise every restart of the flask app would
logout all your users.


You can read more about config values at:
http://python-eve.org/config.html
http://flask.pocoo.org/docs/0.10/config/
http://flask-wtf.readthedocs.org/en/latest/config.html)
http://docs.celeryproject.org/en/latest/configuration.html
