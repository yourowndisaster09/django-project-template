#!/bin/bash -ex

NAME={{ project_name }}
DJANGO_DIR=~/{{ project_name }}/{{ project_name }}
VIRTUALENV_ACTIVATE=~/.virtualenvs/{{ project_name }}/bin/activate
SOCKFILE=/tmp/gunicorn.sock
NUM_WORKERS=3
DJANGO_WSGI_MODULE={{ project_name }}.wsgi
SECRETS=~/.secrets

# Activate the virtual environment
cd $DJANGO_DIR
source $VIRTUALENV_ACTIVATE
source $SECRETS
export PYTHONPATH=$DJANGO_DIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --workers $NUM_WORKERS \
  --log-level=debug \
  --bind=unix:$SOCKFILE
