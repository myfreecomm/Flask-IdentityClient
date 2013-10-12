#!/bin/bash

set -ex

# Initial data
BASE_DIR="$(dirname $0)"
cd "$BASE_DIR/"

virtualenv --no-site-packages --distribute .
. bin/activate
easy_install -U distribute
pip install -r requirements.txt
