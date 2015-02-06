from setuptools import setup, find_packages
from syncanocli import __version__


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='syncanocli',
    version=__version__,
    description='CLI for Syncano',
    long_description=readme(),
    author='Daniel Kopka',
    author_email='daniel.kopka@syncano.com',
    url='http://syncano.com',
    packages=find_packages(),
    test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
    install_requires=[
        'six==1.9.0',
        'click==3.3',
    ],
    tests_require=[
        'mock>=1.0.1',
        'coverage>=3.7.1',
    ],
    entry_points={
        'console_scripts': [
            'syncano = syncanocli.main:cli'
        ]
    }
)
