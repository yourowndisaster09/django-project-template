#!/bin/bash -ex

PROJECT={{ project_name }}
WORKSPACE=~/workspace/{{ project_name }}-ci
DJANGO_DIR=$WORKSPACE/$PROJECT
DJANGO_SETTINGS_MODULE={{ project_name }}.settings.ci
VIRTUALENVWRAPPER=/usr/local/bin/virtualenvwrapper.sh
VIRTUALENV_ACTIVATE=~/.virtualenvs/{{ project_name }}/bin/activate
VIRTUALENV_REQUIREMENTS=$WORKSPACE/requirements/ci.txt 

# Activate the virtual environment
cd $DJANGO_DIR
source $VIRTUALENVWRAPPER
mkvirtualenv --no-site-packages --distribute ${PROJECT}
source $VIRTUALENV_ACTIVATE
pip install -r ${VIRTUALENV_REQUIREMENTS}
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGO_DIR:$PYTHONPATH

# Test django app
python manage.py jenkins
