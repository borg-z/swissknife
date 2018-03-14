#!/bin/bash
python3 -m virtualenv --system-site-packages -p python3 venv
source venv/bin/activate
pip install -r requirements
