#!/usr/bin/env python
import re
import os
import sys
from setuptools import setup, Command
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


class Publish(Command):
    """
    Publish package in local pypi
    """
    description = "Publish package in local pypi"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('python setup.py sdist upload -r internal')
        sys.exit(0)

config = ConfigParser()
config.read_file(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
major_version, minor_version, _ = info.get('version', '0.0.1').split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []

MODULE2PREFIX = {}

MODULE = "{{ cookiecutter.module_name }}"
PREFIX = "{{ cookiecutter.module_prefix }}"
for dep in info.get('depends', []):
    if not re.match(r'(ir|res|webdav)(\W|$)', dep):
        requires.append(
            '%s_%s >= %s.%s, < %s.%s' % (
                MODULE2PREFIX.get(dep, 'trytond'), dep,
                major_version, minor_version, major_version,
                minor_version + 1
            )
        )
requires.append(
    'trytond >= %s.%s, < %s.%s' % (
        major_version, minor_version, major_version, minor_version + 1
    )
)

setup(
    name='%s_%s' % (PREFIX, MODULE),
    version=info.get('version', '0.0.1'),
    description="{{ cookiecutter.description }}",
    author="{{ cookiecutter.author }}",
    author_email='{{ cookiecutter.email }}',
    url='{{ cookiecutter.website }}',
    package_dir={'trytond.modules.%s' % MODULE: '.'},
    packages=[
        'trytond.modules.%s' % MODULE,
        'trytond.modules.%s.tests' % MODULE,
    ],
    package_data={
        'trytond.modules.%s' % MODULE: info.get('xml', []) +
        info.get('translation', []) +
        ['tryton.cfg', 'locale/*.po', 'tests/*.rst', 'reports/*.odt'] +
        ['view/*.xml'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: {{ cookiecutter.licence }} License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    long_description=open('README.rst').read(),
    license='{{ cookiecutter.licence }}',
    install_requires=requires,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    %s = trytond.modules.%s
    """ % (MODULE, MODULE),
    test_suite='tests',
    test_loader='trytond.test_loader:Loader',
    cmdclass={
        'publish': Publish,
    }
)
