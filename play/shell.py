#!/usr/bin/env python3
import argparse
from errno import EEXIST
from getpass import getpass
import os
import sys
from uuid import uuid4

from flask import Config
import pymongo

from play.default_settings import Config as BaseConfig
from play.models.users import hash_password
from play.mongo import ensure_indices

default_config_path = '/etc/play/play.cfg'
default_collections = {'albums', 'artists', 'directories', 'playlists', 'tracks', 'users'}


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def setup(args):
    format = '{}. {}: {}\n'
    arguments = sorted(vars(args).keys())
    arguments.remove('func')
    arguments.remove('config')
    sys.stdout.write('Config values:\n\n')
    for index, arg in enumerate(arguments):
        sys.stdout.write(format.format(index + 1, arg, getattr(args, arg)))
    if(not query_yes_no('Are these information correct '
                        'and you want to write to: {}'.format(args.config), 'no')):
        exit('Cancel to write config file.\n')

    if (os.path.isfile(args.config)):
        sys.stdout.write('File exists {}!!\n'.format(args.config))
        if(not query_yes_no('Do you want to overwrite: {}'.format(args.config), 'no')):
            exit('Cancelled to write config file.\n')
    try:
        pymongo.uri_parser.parse_uri(args.MONGO_URI)['database']
        pymongo.MongoClient(args.MONGO_URI)
    except Exception as e:
        exit('Please correct the mongo URI. Following error occurred. {}\n'.format(str(e)))

    try:
        os.makedirs(os.path.dirname(args.config))
    except OSError as e:
        if e.errno != EEXIST:
            exit(str(e))

    with open(args.config, 'w') as fh:
        for arg in arguments:
            fh.write("%s = %s\n" % (arg, repr(str(getattr(args, arg)))))


def _get_config(file):
    if file and not os.path.isfile(file):
        raise Exception('Config file ({}) does not exist.'.format(file))
    config = Config(os.getcwd())
    config.from_object(BaseConfig)
    if file:
        config.from_pyfile(file)
    return config


def init_db(args):
    collections = set(args.collections)
    try:
        config = _get_config(args.config)
        mongo = pymongo.MongoClient(config.MONGO_URI)
        db = mongo.get_default_database()
        intersection = set(db.collection_names()) & collections
        if not args.force and intersection and not \
                query_yes_no('There are collections which will be recreated.'
                             'All docs will be lost: {}'.format(','.join(intersection)),
                             default='no'):
            raise Exception('Cancel recreate (nothing has been deleted).')
        for collection in collections:
            db.drop_collection(collection)
            db.create_collection(collection)
        ensure_indices(db)
    except Exception as e:
        exit(str(e))


def _get_password():
    while True:
        password = getpass('Please set password:')
        confirm = getpass('Please confirm password:')
        if password != confirm:
            sys.stdout.write('Passwords did not match. Please retry.')
        elif password == '':
            sys.stdout.write('Passwords did not match. Please retry.')
        else:
            return password


def add_user(args):
    try:
        config = _get_config(args.config)
        mongo = pymongo.MongoClient(config.MONGO_URI)
        db = mongo.get_default_database()
        if 'users' not in db.collection_names():
            exit('Users collection does not exist, please run initdb.')
        password = args.password
        if not password:
            password = _get_password()
        user = {
            'name': args.name,
            'roles': args.roles,
            'active': args.active,
            'password': hash_password(password)
        }
        print(db.users.insert_one)
        db.users.insert_one(user)
    except Exception as e:
        exit(str(e))

# create the top-level parser
parser = argparse.ArgumentParser(description='Play CLI tool',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparsers = parser.add_subparsers()

# create the parser for the "setup" command
parser_setup = subparsers.add_parser('setup')
parser_setup.add_argument('--config', type=str, default=default_config_path,
                          help='This file should be readable by celery and the uwsgi processes')
parser_setup.add_argument('--MONGO_URI', type=str, default='mongodb://localhost/play',
                          help='mongodb uri to your server / database')
parser_setup.add_argument('--SECRET_KEY', type=str, default=str(uuid4()),
                          help='A secret key for the session with a decent length.')
parser_setup.add_argument('--WTF_CSRF_SECRET_KEY', type=str, default=str(uuid4()),
                          help='A secret key for the CSRF protection with a decent length .')
parser_setup.set_defaults(func=setup)


# create the parser for initializing the mongodb the first time
parser_init_db = subparsers.add_parser('initdb')
parser_init_db.add_argument('--config', type=str, default=default_config_path,
                            help='File to read config from.')
parser_init_db.add_argument('--force', action='store_true', default=False,
                            help='Force deletion of all collections without furhter asking.')
parser_init_db.add_argument('--collections', nargs='+', type=str, choices=default_collections,
                            default=default_collections, help='Collections to be created.')
parser_init_db.set_defaults(func=init_db)


parser_user = subparsers.add_parser('adduser')
parser_user.add_argument('name', type=str,
                         help='Username to be created or updated.')
parser_user.add_argument('--password', type=str, default=None,
                         help='Password to set')
parser_user.add_argument('--active', dest='active', action='store_true')
parser_user.add_argument('--inactive', dest='active', action='store_false')
parser_user.set_defaults(active=True)
parser_user.add_argument('--roles', nargs='*', type=str,
                         default=['admin'], help='Known roles are admin, user')
parser_user.add_argument('--config', type=str, default=default_config_path,
                         help='File to read config from.')
parser_user.set_defaults(func=add_user)


def main():  # nocov
    args = parser.parse_args()
    if getattr(args, 'func', None):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':  # nocov
    main()
