#!/bin/bash -ex
#
# Will be run by Jenkins lnp-staging project
# Depends on lnp project
#

cd ~/jobs/lnp-production/workspace
source ~/.virtualenvs/lnp/bin/activate
fab set_env:production production
