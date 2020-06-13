[![Build Status](https://travis-ci.org/pmatigakis/hnac.svg?branch=develop)](https://travis-ci.org/pmatigakis/hnac)

Introduction
============

Hnac is a crawler for the hackernews firebase API.

Installation
============

Create a virtualenv

    virtualenv --python=python3 virtualenv
    source virtualenv/bin/activate

Install the package

    python setup.py install

Usage
=====

Create the configuration file *settings.py* and set the variables for the Postgresql
database.

```python
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://username:password@localhost:5432/hnac"
```

Edit the alembic.ini file and set the *sqlalchemy.url* variable to point to your
database. Run the migrations.

```
alembic upgrade head
```

Create a user so that it is possible to access the API

```
hnac users create --username username --password user_password
```

Start the API server

```
hnac runserver
```

You can crawl hacker news using the *crawl* command. You should create a cron
job that will execute this command in a time interval of your choosing

```
hnac crawl
```

You can enable additional handlers in order to save the hackernews stories on
a CouchDB database or publish them on RabbitMQ. See the example `settings.py` file
in the `templates` folder for an example on how to use them.

Api
===
TODO
