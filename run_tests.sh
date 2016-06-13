#!/bin/bash

set -e

flake8 .
isort --recursive --check-only .

coverage run -m unittest discover -p 'test*.py'
coverage html -d coverage/unittest
