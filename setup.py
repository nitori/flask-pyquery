"""
flask-pyquery
----------
This extension for the `Flask <http://flask.pocoo.org/>`_ micro web framework
allows developers to use  `PyQuery Templates
<http://http://www.makotemplates.org/>`_ instead of the default Jinja2
templating engine.
"""
import sys
from setuptools import setup

setup(
    name='Flask-PyQuery',
    version='0.1',
    url='https://github.com/knitori/flask-pyquery',
    license='BSD',
    author='Nitori Kawashiro',
    author_email='nitori@chireiden.net',
    description='PyQuery templating support for Flask applications.',
    long_description=__doc__,
    py_modules=['flask_pyquery'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'lxml',
        'pyquery',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
