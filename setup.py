import os

from setuptools import find_packages, setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='syncano-cli',
    version='0.3',
    description='Syncano command line utilities',
    long_description=README,
    author='Marcin Swiderski, Sebastian Opalczynski',
    author_email='marcin.swiderski@syncano.com, sebastian.opalczynski@syncano.com',
    url='https://github.com/Syncano/syncano-cli',
    packages=find_packages(),
    license='MIT',
    install_requires=['syncano>=5.1.0', 'PyYaml>=3.11'],
    test_suite='tests',
    tests_require=['mock'],
    entry_points="""
        [console_scripts]
        syncano=syncano_cli.main:main
    """
)
