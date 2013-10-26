"""CI settings and globals."""


from base import *


# DEBUG CONFIGURATION
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# DATABASE CONFIGURATION
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

# DJANGO-JENKINS CONFIGURATION
INSTALLED_APPS += (
    'django_jenkins',
)
PROJECT_APPS = LOCAL_APPS
JENKINS_TASKS = (
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.run_pylint',
    'django_jenkins.tasks.dir_tests',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_jshint',
    'django_jenkins.tasks.run_csslint',
    'django_jenkins.tasks.run_sloccount',
)
JSHINT_CHECKED_FILES = STATICFILES_DIRS
CSSLINT_CHECKED_FILES = STATICFILES_DIRS
