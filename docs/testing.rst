Running the Tests
=================
Play is running with Python 3.4 other environments are currently untested.
Therefore tests will be run in those four platforms in our `CI server`_.

The tests are using tox_ for full automatic testing and tox_ uses `py.test`_ to run the tests.
It also runs flake for pep8 checking / linting.


Running the Tests with `tox`_
_____________________________

.. code-block:: console

   $ tox

For more command line parameters please refer to the tox_ documentation.

Running the Tests with `tox`_
_____________________________

You should create a virtual environment before test and installing py.test.

Create your python3.4 environment and activate it.
Afterwards you could use the following to prepare the environment to
run the tests.

.. code-block:: console

   $(virtualenv) pip install -U pip
   $(virtualenv) pip install -r requirements.txt
   $(virtualenv) pip install -r test-requirements.txt


.. code-block:: console

   $ py.test ./tests

For more command line parameters please refer to the `py.test`_ documentation.


Running tests against a mock or a real mongodb:
_______________________________________________

Humongous_ is used to load fixtures and a database into a mongomock or a real mongodb.
You can switch the type of database by:

.. code-block:: console

   $ tox -e py34 -- --humongous_engine=mongomock

This uses a real mongo:

.. code-block:: console

   $ tox -e py34 -- --humongous_engine=pymongo --humongous_host
It is currently not possible to switch the database name, it has to be 'play'.

Commands for py.test:

.. code-block:: console

   $ py.test ./tests --humongous_engine=mongomock


.. code-block:: console

   $ py.test ./tests --humongous_engine=pymongo --humongous_host

.. _humongous: https://github.com/mdomke/humongous
.. _`py.test`: http://pytest.org/latest/
.. _`CI server`: https://travis-ci.org/julianhille/play/
.. _tox: http://tox.readthedocs.org/en/latest/
.. _MongoDb:  https://www.mongodb.org/

