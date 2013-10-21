#!/bin/bash -ex

mkvirtualenv {{ project_name }}
pip install -r requirements/production.txt
python manage.py syncdb --noinput
python manage.py migrate
python manage.py jenkins --all
