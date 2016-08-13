from setuptools import setup, find_packages


setup(
    name="hnac",
    description = "Crawler for the Hackewnews API",
    author = "Panagiotis Matigakis",
    author_email = "pmatigakis@gmail.com",
    version="0.1",

    packages=find_packages(),

    install_requires=[
        "python-firebase==1.2",
        "SQLAlchemy==1.0.13",
        "Flask==0.11.1",
        "flask-restplus==0.9.2",
        "marshmallow==2.9.1",
        "Flask-Script==2.0.5",
        "Flask-Login==0.3.2",
        "Flask-WTF==0.12",
        "CouchDB==1.1",
        "Flask-RESTful==0.3.5"
    ],
    
    tests_require=[
        "nose==1.3.7",
        "httpretty==0.8.14"
    ],

    test_suite = 'nose.collector',

    entry_points = {
        'console_scripts': [
            'hnac_start_crawler=hnac.cli.cli:start_crawler',
            'hnac=hnac.cli.cli:main'
        ]
    },
      
    zip_safe=False,

    include_package_data=True,
    package_data={
      'hnac': ['web/templates/*.html'],
    }
)
