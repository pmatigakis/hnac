Installation
============

Create a virtualenv

    virtualenv --python=python2.7 virtualenv
    source virtualenv/bin/activate

Install the package

    python setup.py install

Usage
=====

Create the configuration file

    hnac_create_configuration

Open the *hnac.ini* file and adjust the settings 

Start the crawler

    hnac_start_crawler

Start the API server

    hnac_start_api_server
