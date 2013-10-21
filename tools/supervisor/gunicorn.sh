#!/bin/bash

. ~/.secrets
~/.virtualenvs/{{ project_name }}/bin/python manage.py run_gunicorn -b 'unix:/tmp/gunicorn.sock'
