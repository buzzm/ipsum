Development
===========

Install dev environment
-------------------------

Fork the project

.. code-block:: console

    $ make install
    $ # choose and activate your python virtualenv

Tests
------

Tests against Docker MongoDB
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Change image tag as needed. Avoid the use of 'latest' tag.

.. code-block:: console

    (.venv) $ docker pull mongo:7.0.2
    (.venv) $ docker container run --rm -dti --name mongo-test -p 127.0.0.1:27017:27017 mongo:7.0.2
    (.venv) $ mongo_ipsum --upload --drop --count 1 src/mongo_ipsum/models/hello.jsch
