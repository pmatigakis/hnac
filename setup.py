from setuptools import setup, find_packages


setup(
    name="hnac",
    description = "Crawler for the Hackewnews API",
    author = "Panagiotis Matigakis",
    author_email = "pmatigakis@gmail.com",
    version="0.3.0",

    packages=find_packages(),

    install_requires=[
        "python-firebase==1.2",
        "Flask==0.11.1",
        "marshmallow==2.10.1",
        "Flask-Script==2.0.5",
        "Flask-Login==0.3.2",
        "Flask-WTF==0.12",
        "CouchDB==1.1",
        "Flask-RESTful==0.3.5",
        "Flask-JWT==0.3.2",
        "alembic==0.8.8",
        "psycopg2==2.7.3.2",
        "Flask-Admin==1.4.2",
        "uWSGI==2.0.14",
        "pika==0.10.0",
        "arrow==0.12.1",
        "Flask-SQLAlchemy==2.3.2"
    ],
    
    tests_require=[
        "nose==1.3.7",
        "httpretty==0.8.14"
    ],

    test_suite='nose.collector',

    entry_points={
        'console_scripts': [
            'hnac=hnac.cli.cli:main'
        ]
    },
      
    zip_safe=False,

    include_package_data=True
)
