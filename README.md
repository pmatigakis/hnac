Installation
============

Create a virtualenv

    virtualenv --python=python2.7 virtualenv
    source virtualenv/bin/activate

Install the package

    python setup.py install

Usage
=====

Create the configuration file *settings.py* and set the variables for the sqlite
database and the Couchdb database

```python
DB = "sqlite:////path/to/database/hnac.db"

COUCHDB_SERVER = "http://localhost:5984"
COUCHDB_DATABASE = "hnac"
```

Initialize the database

```
hnac initdb
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
