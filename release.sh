#!/bin/bash

cat > ~/.pypirc <<EOF
[distutils] # this tells distutils what package indexes you can push to
index-servers = pypi

[pypi]
repository: https://pypi.python.org/pypi
username: ${PYPI_USER}
password: ${PYPI_PASSWORD}
EOF

python setup.py register -r pypi
python setup.py sdist upload -r pypi
