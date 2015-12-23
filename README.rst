Teacher's Portal
================
.. image:: https://travis-ci.com/mitodl/teachersportal.svg?token=XTpdxUNyGRQG4uuk8RkK
    :target: https://travis-ci.com/mitodl/teachersportal

.. image:: https://www.herokucdn.com/deploy/button.png
    :target: https://heroku.com/deploy


Getting Started
---------------

You can either run teachersportal locally with a default sqlite database after
installing the ``requirements.txt`` file, or if you have Docker and
prefer a cleaner environment, install ``docker-compose`` with ``pip
install docker-compose`` and run ``docker-compose up``. This will set
up a near production-ready containerized development environment that
runs migrations, with the Django development server running on
port ``8075``.

To run one-off commands, like shell, you can run::

  docker-compose run web python manage.py shell

or to create root user::

  docker-compose run web python manage.py createsuperuser


For OS X Development
--------------------

Due to issues using Docker in OSX, development is more efficient if you
install `docker-osx-dev <https://github.com/brikis98/docker-osx-dev>`_.
``docker-osx-dev`` keeps host file system changes synced to the Docker
container. You can install it by typing ``make`` once you have created the
Docker container.

Subsequently, before you start your Docker container with
``docker-compose up``, you would run::
  
     docker-osx-dev -m default -s ./

(Assuming your Docker VM is called ``default``, and your current working
directory is the root of the ``teachersportal`` source directory).

This starts a process that monitors the file system for changes. On startup
you may receive this error::
  
      [ERROR] Found VirtualBox shared folders on your Boot2Docker VM. These may
      void any performance benefits from using docker-osx-dev:
      
      /Users
      
      [INSTRUCTIONS] Would you like this script to remove them?
      1) yes
      2) no

Answer ``yes``.

Configuration and Start-up
--------------------------

1. Copy the ``.env.sample`` file to ``.env`` and edit these values::

     CCXCON_API="<url of your ccxcon instance>"
     CCXCON_OAUTH_CLIENT_ID="<client id of your ccxcon oauth application>"
     CCXCON_OAUTH_CLIENT_SECRET="<client secret of your ccxcon oauth application>"

#. (OSX only) Create your docker machine::

     docker-machine create default
     docker-machine start default
     docker-machine env default
     eval "$(docker-machine env default)"

   These commands create a Docker container named ``default``, start the
   container, and configure environment variables to facilitate communication
   with ``ccxcon``.

#. Create a user who has permission to view the course::

     docker-compose run web python manage.py createsuperuser

#. Start the machine::

     docker-compose up

#. visit: http://192.168.99.100:8075/

.. note:: (OSX only)

  Your IP address may vary depending on what address docker assigns to your VM.
  If the IP above doesn't work:

  1. Power down your docker-machine (``docker-machine stop default``)
  2. ``docker-machine ssh default``
  3. Once in the docker machine shell, run ``ifconfig``, and look for
     the IP address that begins with ``192.168.99.xxx``.

- Click the login button on the TP UI and put in the user credentials
  you created in step 3.
- browse https://ccxcon-ci.herokuapp.com, and choose a course uuid,
  you can view that course in ``teachersportal``:
  https://url.of.your.ccxcon/api/v1/coursexs/
- Now visit: http://192.168.99.100:8075/courses/asdf-asdf-asdf
  (or whatever the uuid is that you selected).

Dev Tools
---------

This project uses
`react-devtools <https://github.com/gaearon/redux-devtools>`_.
``react-devtools`` help you debug actions and mutations to
the underlying redux store. To enable it, press ``Ctrl+H`` in the browser. 
You can then click the action names to undo or redo them.

Adding an Application
---------------------

To add an application to Teacher's Portal, add it to ``requirements.txt``,
add its needed settings, include its URLs, and provide any needed template
overrides.

Testing
-------

The project is set up with
`tox <https://tox.readthedocs.org/en/latest/>`_ and
`py.test <http://pytest.org/latest/>`_. It will run pylint, pep8, and
py.test tests with coverage. It will also generate an HTML coverage
report. To run them all inside the Docker image, run ``docker-compose
run web tox``, or if you are running locally, after installing the
requirements file, just run ``tox``.

Continuous Testing
~~~~~~~~~~~~~~~~~~

If you want to run tests when files change, the ``test_requirements.txt``
adds pytest-watcher, which can be started with ``ptw``. This
unfortunately will not work well in the Docker container because the
file events it uses are fired on the host OS, and not the Docker OS. I
have corrected it upstream with
`issue <https://github.com/joeyespo/pytest-watch/issues/9>`_ to the
`pytest-watch repo <https://github.com/joeyespo/pytest-watch>`_, but it
has not been released to pypi as of this writing.

How it works
============

This describes how the full system works with regards to edX and the
Teacher's Portal (listed as TP for the rest of this document). The
system is designed to work with multiple edX backends and multiple
clients beyond TP, but this should provide a reasonable sense for how
things work at a high level.

Initial App Setup
-----------------

We need to generate users and keys for all clients of CCXcon. This is
done in the Django admin. We pass those credentials to edX and TP who
will use them for making requests.

Getting the course to Teacher's Portal
--------------------------------------

When the user lists a course as enabled for CCX and inputs a CCXcon
advanced setting, the course is exportable to CCXcon.

Any publishes of this course will post updates to CCXCon
asynchronously, using the credentials given to edX initially.

Upon receipt, CCXCon will make its own async post to any number of
backends (e.g. TP).

From this point, the course is in the TP database. Its users can
toggle its visibility after setting prices.

.. image:: figures/course-creation.png

Login Flow
----------

When a CCX is marked as "enabled for CCX", we generate an anonymous
user id for each admin user of the course. This gets sent along with
the create payload to CCXCon. Additionally, we generate an email with
a login link to TP for the user.

When the user clicks the link, they're taken to a login/register page
on TP. Upon successful login/creation, TP queries CCXCon for which
course this belongs to. If it finds a user, the account is linked on
the TP side. All subsequent API requests are filtered by these
credentials as necessary. CCXCon does *NOT* handle authorization
checks.

.. image:: figures/login-flow.png

Course Listings
---------------

When doing a public course listing, the javascript front-end queries TP
for available courses (as determined by the django-oscar ``Product``
model). This returns ids to look up. From here, the javascript
dispatches an additional API call to CCXCon to get detail on those
specific course ids for populating the UI.

In the instructor dashboard case (privileged, unpublished course
listing), we validate they're a course owner on TP, then issue a fetch
for their known course ids (using the mapping table we've generated on
TP from them clicking the login links edX emailed them) on CCXCon.

.. image:: figures/course-listing.png

Order Fulfillment on Teacher's Portal
-------------------------------------

Order fulfillment will result in a user with a CCX on edX (or some
similar backend instance) with a limited set of seats.

Upon checking out and paying for the course, TP issues a RPC to 
create a CCX for the user making the purchase with the seat count 
in the order. This synchronously posts the command to edX and handles 
the creation.

Updating previous order
-----------------------

Users can purchase additional seats, so it's important that TP keep
track of seat count purchases.

If the teacher has bought a course and views it again, the buy slider
is already selected to the seat count they've purchased. It can't go
lower than that number. If they drag it to buy more seats and
purchase, we make a synchronous patch to edX via CCXCon to update this
seat count listing.
