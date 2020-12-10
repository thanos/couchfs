#!/usr/bin/env python

"""The setup script."""
import warnings
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', 'requests>=2.25.0', 'humanize>=3.1.0']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', 'requests-mock==1.8.0', 'coverage==4.5.4']

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
#         from couchfs.api import CouchDBClient, URLRequired
#         try:
#             print('connecting to couchdb')
#             client = CouchDBClient()
#             print('checking the db')
#             if not client.check_db():
#                 print('creating the db')
#                 client.create_db()
#         except URLRequired as e:
#             print(f'''
# THE INSTALLION WAS NOT COMPLETE:
#     It is best if you have access to a couchdb instance.
#     set th87e environment variable {CouchDBClient.URI_ENVIRON_KEY} as documented:
#     export COUCHDB_URI='couchdb://username:password@host:port/database'
#     then when you rerun install. Then setup.py will install a couchdb view that it uses to index your attachments in that database.
#             ''')





setup(
    author="thanos vassilakis",
    author_email='thanosv@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="a couchdb user space (FUSE) file system plus a cli for treating couchdb databases as a file system drives",
    entry_points='''
        [console_scripts]
        couchfs=couchfs.cli:couchfs
    ''',
    cmdclass={
            'develop': PostDevelopCommand,
            'install': PostInstallCommand,
        },

    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='couchfs',
    name='couchfs',
    packages=find_packages(include=['couchfs', 'couchfs.*']),
    setup_requires=setup_requirements,
    extras_require = {
            'full': ['refuse',]
        },
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/thanos/couchfs',
    version='0.1.2',
    zip_safe=False,
)
