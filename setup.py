import os
from setuptools import find_packages, setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

setup(
    name='syncano-cli',
    version='0.3',
    description='Syncano command line utilities',
    long_description=README,
    author='Marcin Swiderski',
    author_email='marcin.swiderski@syncano.com',
    url='https://github.com/Syncano/syncano-cli',
    packages=find_packages(),
    license='MIT',
    install_requires=['syncano>=5.0', 'PyYaml>=3.11'],
    test_suite='tests',
    entry_points="""
        [console_scripts]
        syncano=syncano_cli.main:main
    """
)
