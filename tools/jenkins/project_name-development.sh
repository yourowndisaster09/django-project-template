#!/bin/bash -ex
#
# Will be run by Jenkins lnp-testing project
# Depends on lnp project
#

cd ~/jobs/lnp/workspace
source ~/.virtualenvs/lnp/bin/activate
fab set_env:testing testing
