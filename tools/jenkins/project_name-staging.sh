#!/bin/bash -ex
#
# Will be run by Jenkins lnp-staging project
# Depends on lnp project
#

cd ~/jobs/lnp-staging/workspace
source ~/.virtualenvs/lnp/bin/activate
fab set_env:staging staging
