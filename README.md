Introduction
============

Hnac is a crawler for the hackernews firebase API.

Installation
============

Create a virtualenv

    virtualenv --python=python2.7 virtualenv
    source virtualenv/bin/activate

Install the package

    python setup.py install

Usage
=====

Create the configuration file *settings.py* and set the variables for the Postgresql
database and the Couchdb database

```python
DB = "postgresql+psycopg2://username:password@localhost:5432/hnac"

COUCHDB_SERVER = "http://localhost:5984"
COUCHDB_DATABASE = "hnac"
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

Api
===
TODO
