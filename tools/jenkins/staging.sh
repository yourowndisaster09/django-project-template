#!/bin/bash -ex

PROJECT={{ project_name }}
WORKSPACE=~/workspace/{{ project_name }}-staging
VIRTUALENVWRAPPER=/usr/local/bin/virtualenvwrapper.sh

# Activate the virtual environment
cd $WORKSPACE
source $VIRTUALENVWRAPPER
workon ${PROJECT}

# Deploy development
fab staging deploy
