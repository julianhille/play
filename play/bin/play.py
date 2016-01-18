#!/usr/bin/env python3
import argparse
from configparser import ConfigParser
from errno import EEXIST
import os
import sys
from uuid import uuid4

import pymongo


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

    parser = ConfigParser()
    for arg in arguments:
        parser.set('DEFAULT', arg, str(getattr(args, arg)))
    with open(args.config, 'w') as fh:
        parser.write(fh)


# create the top-level parser
parser = argparse.ArgumentParser(description='Play CLI tool',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparsers = parser.add_subparsers()

# create the parser for the "setup" command
parser_setup = subparsers.add_parser('setup')
parser_setup.add_argument('--config', type=str, default='/etc/play/play.ini',
                          help='This file should be readable by celery and the uwsgi processes')
parser_setup.add_argument('--MONGO_URI', type=str, default='mongodb://localhost/play',
                          help='mongodb uri to your server / database')
parser_setup.add_argument('--SECRET_KEY', type=str, default=str(uuid4()),
                          help='A secret key for the session with a decent length.')
parser_setup.add_argument('--WTF_CSRF_SECRET_KEY', type=str, default=str(uuid4()),
                          help='A secret key for the CSRF protection with a decent length .')

parser_setup.set_defaults(func=setup)


if __name__ == '__main__':  # nocov
    args = parser.parse_args()
    if getattr(args, 'func', None):
        args.func(args)
    else:
        parser.print_help()
