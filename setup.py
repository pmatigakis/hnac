from setuptools import setup, find_packages


def read_requirements(requirements_file):
    with open(requirements_file) as f:
        return [
            line.strip()
            for line in f
        ]


setup(
    name="hnac",
    description = "Crawler for the Hackernews API",
    author = "Panagiotis Matigakis",
    author_email = "pmatigakis@gmail.com",
    version="0.7.0",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),
    tests_require=read_requirements("requirements-test.txt"),
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'hnac=hnac.cli.cli:main'
        ]
    },
    zip_safe=False,
    include_package_data=True
)
