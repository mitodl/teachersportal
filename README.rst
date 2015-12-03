teachersportal
--------

Teacher's Portal

.. image:: https://travis-ci.com/mitodl/teachersportal.svg?token=XTpdxUNyGRQG4uuk8RkK
    :target: https://travis-ci.com/mitodl/teachersportal

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy


Getting Started
===============

You can either run this locally with a default sqlite database after
installing the requirements.txt file, or if you have Docker and
prefer a cleaner environment, install docker-compose with ``pip
install docker-compose`` and run ``docker-compose up``. This will set
up
a near production-ready containerized development environment that
runs migrations, with the django development server running on
port 8075.

To run one-off commands, like shell, you can run
``docker-compose run web python manage.py shell`` or to create root
user, etc.

For OS X development
====================

Install docker-osx-dev before starting.

You can do that by typing `make` after you set up your docker
container for the first time.

Subsequently, before you start up your docker container with
docker-compose up, you would run: docker-osx-dev -m default -s ./
(if your docker VM is called `default`, and your CWD is the
root of the teachers portal source directory).

Dev Tools
=========

`react-devtools <https://github.com/gaearon/redux-devtools>` is in use
on this repository. This will help you debug actions and mutations to
the underlying redux store. To enable it, press `Ctrl+H`. You can then
click the action names to undo or redo them.


Adding an application
=====================

To add an application to this, add it to the requirements file, add
its needed settings, include its URLs, and provide any needed template
overrides.


Testing
=======

The project is set up with
`tox<https://tox.readthedocs.org/en/latest/>`_ and
`py.test<http://pytest.org/latest/>`_. It will run pylint, pep8, and
py.test tests with coverage. It will also generate an HTML coverage
report. To run them all inside the docker image, run ``docker-compose
run web tox``, or if you are running locally, after installing the
requirements file, just run ``tox``.

Continuous Testing
~~~~~~~~~~~~~~~~~~

If you want test to run on file changes, the ``test_requirements.txt``
adds pytest-watcher, which can be started with ``ptw``. This
unfortunately will not work well in the Docker container because the
file events it uses are fired on the host OS, and not the docker OS. I
have corrected it upstream with
`issue<https://github.com/joeyespo/pytest-watch/issues/9>`_ to the
`pytest-watch repo<https://github.com/joeyespo/pytest-watch>`_, but it
has not been released to pypi as of this writing.
