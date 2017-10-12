from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

setup(

    name='cryptolens',
    version='0.1.12',
    description = 'Command line tool to monitor the prices of cryptocurrencies',
    url='https://github.com/hkilian/cryptolens',
    author = 'Harry Kilian',
    author_email = 'harrykilian@gmail.com',
    license='MIT',

    python_requires='>=3',

    include_package_data=True,

    install_requires=[
          'urwid',
          'sortedcontainers',
          'fuzzywuzzy',
          'websockets',
          'requests',
          'peewee',
      ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='sample setuptools development',

    entry_points={
       'console_scripts': [
           'cryptolens = cryptolens.main:main',
           'crypto = cryptolens.main:main',
       ],
    },
    
    packages=['cryptolens', 'cryptolens.mvc', 'cryptolens.core', 'cryptolens.daemon', 'cryptolens.exchanges'],

)

