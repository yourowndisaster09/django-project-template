# Django + nginx + git + postgresql + memcached + supervisor

from os.path import dirname, join
from sys import path

from fabric.api import env, settings
from fabric.context_managers import cd, hide, prefix
from fabric.contrib import django
from fabric.contrib.console import confirm
from fabric.contrib.files import contains, exists, sed
from fabric.operations import put, run, sudo


FAB_ROOT = dirname(__file__)
path.append(FAB_ROOT)

PROJECT = 'jajomaxx'
REPOSITORY = 'git@bitbucket.org:softwarelab7/jajomaxx.git'
VIRTUALENV = 'jajomaxx'
ADDITIONAL_PACKAGES = [
    'mercurial',
    'libjpeg8-dev', 
    'zlib1g-dev', 
    'libfreetype6-dev', 
    'liblcms1-dev'
]

CI_KEY_FILENAME = 'jajomaxx-ci.pem'
CI_KEY_FILE_LOCAL_LOCATION = '~/.ssh/jajomaxx-ci.pem'
CI_HOST = 'ubuntu@ec2-54-244-180-233.us-west-2.compute.amazonaws.com'
CI_SETTINGS_PATH = 'jajomaxx.jajomaxx.settings.ci'

DEVELOPMENT_KEY_FILENAME = 'jajomaxx-development.pem'
DEVELOPMENT_KEY_FILE_LOCAL_LOCATION = '~/.ssh/jajomaxx-development.pem'
DEVELOPMENT_HOST = 'ubuntu@ec2-54-244-194-210.us-west-2.compute.amazonaws.com'

STAGING_KEY_FILENAME = ''
STAGING_KEY_FILE_LOCAL_LOCATION = ''
STAGING_HOST = ''

PRODUCTION_KEY_FILENAME = ''
PRODUCTION_KEY_FILE_LOCAL_LOCATION = ''
PRODUCTION_HOST = ''


####################################
## Local Access to remote servers ##
####################################

def ci():
    """
    Access ci server locally
    
    """
    env.key_filename = CI_KEY_FILE_LOCAL_LOCATION
    env.host_string = CI_HOST
    env.env_name = 'ci'

def development():
    """
    Access development server locally
    
    """
    env.key_filename = DEVELOPMENT_KEY_FILE_LOCAL_LOCATION
    env.host_string = DEVELOPMENT_HOST
    env.env_name = 'development'
    
def staging():
    """
    Access staging server locally
    
    """
    env.key_filename = STAGING_KEY_FILE_LOCAL_LOCATION
    env.host_string = STAGING_HOST
    env.env_name = 'staging'
    
def production():
    """
    Access production server locally
    
    """
    env.key_filename = PRODUCTION_KEY_FILE_LOCAL_LOCATION
    env.host_string = PRODUCTION_HOST
    env.env_name = 'production'


##################################
## Ubuntu packages installation ##
##################################

def install_jenkins():
    run('wget -q -O - http://pkg.jenkins-ci.org/debian/jenkins-ci.org.key | sudo apt-key add -')
    sudo('sh -c "echo deb http://pkg.jenkins-ci.org/debian binary/ > /etc/apt/sources.list.d/jenkins.list"')
    sudo('apt-get update')
    sudo('apt-get install jenkins')
    
def install_git():
    sudo('apt-get install git')
    
def install_nginx():
    sudo('add-apt-repository -y ppa:nginx/stable')
    sudo('apt-get update')
    sudo('apt-get -y install nginx')
    
def install_postgres():
    sudo('apt-get -y install python-setuptools libpq-dev python-dev')
    sudo('apt-get -y install postgresql-9.1 python-psycopg2')
    
def install_memcached():
    sudo('apt-get -y install memcached')
    
def install_supervisor():
    sudo('apt-get -y install supervisor')
    
def install_virtualenvwrapper():
    sudo('apt-get install -y python-pip')
    sudo('pip install virtualenvwrapper')
    
def install_additional_packages():
    if ADDITIONAL_PACKAGES:
        sudo("apt-get -y install %s" % " ".join(ADDITIONAL_PACKAGES))
        
        
######################
## Service commands ##
######################
    
def nginx(cmd):
    sudo('service nginx %s' % cmd)
    
def postgresql(cmd):
    sudo('service postgresql %s' % cmd)
    
def memcached(cmd):
    sudo('service memcached %s' % cmd, pty=False)
    
def supervisor(cmd):
    sudo('service supervisor %s' % cmd)


##############################
## Postgres database setups ##
##############################
def setup_database(name, user, password, test=False):
    """
    Creates a postgres database
    
    """
    if test:
        name = 'test_' + name
        
    with settings(warn_only=True):
        sudo('psql -c "CREATE ROLE {0} WITH PASSWORD \'{1}\' NOSUPERUSER CREATEDB NOCREATEROLE LOGIN;"'.format(user, password), user='postgres')
        sudo('psql -c "CREATE DATABASE {0} WITH OWNER={1} TEMPLATE=template0 ENCODING=\'utf-8\';"'.format(name, user), user='postgres')
        if test:
            sudo('psql -c "ALTER USER {0} CREATEDB;"'.format(user), user='postgres')
    
    pg_hba_location = '/etc/postgresql/9.1/main/pg_hba.conf'
    if contains(pg_hba_location, 'peer', use_sudo=True):
        sed(pg_hba_location, 'peer', 'trust', use_sudo=True)
        postgresql('restart')
            
def setup_database_from_secrets(test=False):
    """
    Gets database configurations from environment variables set in secrets
    
    """
    with settings(hide('everything')):
        with prefix('source ~/.secrets'):
            name = run('echo $DATABASE_NAME')
            user = run('echo $DATABASE_USER')
            password = run('echo $DATABASE_PASSWORD')
    setup_database(name, user, password, test)
    
def setup_database_from_settings(settings_path, test=False):
    """
    Gets database configurations from local django settings file
    
    """
    django.settings_module(settings_path)
    from django.conf import settings as djangosettings
    database = djangosettings.DATABASES.get('default')
    name = database.get('NAME')
    user = database.get('USER')
    password = database.get('PASSWORD')
    setup_database(name, user, password, test)
    
    
#####################################
## Remote environment server utils ##
#####################################

def upload_secrets(secret_file):
    """
    Upload secret file to remote server
    
    """
    put(secret_file, '~/.secrets')

def add_pub_key():
    """
    Generate pub key as git deployment key
    
    """
    if env.env_name == 'ci':
        env.pubkey = '/var/lib/jenkins/.ssh/id_rsa.pub'
        user = 'jenkins'
    else:
        env.pubkey = '/home/ubuntu/.ssh/id_rsa.pub'
        user = None
    
    pubkey_exists = False
    if exists(env.pubkey, use_sudo=True):
        pubkey_exists = True
        if confirm('Pub key already exists. Overwrite?'):
            pubkey_exists = False
    if not pubkey_exists:
        sudo('ssh-keygen', user=user)
    sudo('cat %(pubkey)s' % env, user=user)
    if confirm('Update as deployment key? Make sure you added the public key as deployment key on bitbucket...'):
        sudo('git ls-remote -h %s HEAD' % REPOSITORY, user=user)

def initialize_variables(env_name):
    env.env_name = env_name
    env.project = PROJECT
    env.virtualenv = VIRTUALENV
    env.repository = REPOSITORY
    
    # Local directories
    env.ssh_dir = '~/.ssh'
    
    # Remote directories
    env.home = '/home/ubuntu'
    env.project_root = join(env.home, env.project)
    env.django_root = join(env.project_root, env.project)
    env.virtualenv_dir = join(env.home, '.virtualenvs', env.virtualenv)
    
def connect():
    """
    If not connecting from the ci server, we assume 
    your pub key is placed in the ssh directory.
    
    """
    if env.env_name == 'development':
        env.key_filename = join(env.ssh_dir, DEVELOPMENT_KEY_FILENAME)
        env.host_string = DEVELOPMENT_HOST
    elif env.env_name == 'staging':
        env.key_filename = join(env.ssh_dir, STAGING_KEY_FILENAME)
        env.host_string = STAGING_HOST
    elif env.env_name == 'production':
        env.key_filename = join(env.ssh_dir, PRODUCTION_KEY_FILENAME)
        env.host_string = PRODUCTION_HOST
    
def install_dependencies():
    install_git()
    install_nginx()
    install_virtualenvwrapper()
    install_postgres()
    install_memcached()
    install_supervisor()
    install_additional_packages()
    
def create_virtualenv():
    with settings(warn_only=True):
        if not exists(env.virtualenv_dir):
            with prefix('source /usr/local/bin/virtualenvwrapper.sh'):
                run('mkvirtualenv --no-site-packages --distribute %(virtualenv)s' % env)
    
def install_django_packages():
    with cd(env.project_root):
        with prefix('source %(virtualenv_dir)s/bin/activate' % env):
            run('pip install -r requirements/%(env_name)s.txt' % env)
            
def get_project_from_repo():
    if not exists(env.project_root):
        run('git clone %(repository)s' % env)
    else:
        with cd(env.project_root):
            run('git pull')
            
def prepare_django_project():
    with prefix('source %(virtualenv_dir)s/bin/activate' % env):
        with cd(env.django_root):
            with prefix('source ~/.secrets'):
                run('python manage.py syncdb --noinput')
                run('python manage.py migrate --noinput')
                run('python manage.py collectstatic --noinput')
            
def prepare_log_directory():
    sudo('mkdir -p /var/log/%(project)s' % env)
    
def setup_env_supervisor():
    with cd(env.project_root):
        supervisor('stop')
        sudo('cp tools/supervisor/%(env_name)s.conf /etc/supervisor/conf.d/%(project)s.conf' % env)
        supervisor('start')
        
def setup_env_memcache():
    with cd(env.project_root):
        sudo('cp tools/memcached/%(env_name)s.conf /etc/memcached.conf' % env)
        memcached('restart')
        
def setup_env_nginx():
    with cd(env.project_root):
        sudo('cp tools/nginx/%(env_name)s /etc/nginx/sites-available/%(project)s' % env)
        sudo('ln -sf /etc/nginx/sites-available/%(project)s /etc/nginx/sites-enabled/' % env)
        nginx('restart')
    
def deploy(env_name):
    """
    Deploy an environment.
    
    """
    initialize_variables(env_name)
    connect()
    
    get_project_from_repo()
    setup_database_from_secrets()
    
    create_virtualenv()
    install_django_packages()
    prepare_django_project()
    
    prepare_log_directory()
    
    setup_env_supervisor()
    setup_env_memcache()
    setup_env_nginx()
    

####################################
## Jenkins server setup specifics ##
####################################

def upload_ci_nginx_settings():
    put('tools/nginx/ci', '/etc/nginx/sites-available/jenkins', use_sudo=True)
    sudo('ln -sf /etc/nginx/sites-available/jenkins /etc/nginx/sites-enabled/')
    
def upload_env_keys():
    """
    Uploads environment keys to ssh folder in ci server
    
    """
    if DEVELOPMENT_KEY_FILE_LOCAL_LOCATION:
        put(DEVELOPMENT_KEY_FILE_LOCAL_LOCATION, use_sudo=True)
        with settings(warn_only=True):
            sudo('ssh -o "StrictHostKeyChecking no" %s' % DEVELOPMENT_HOST, user='jenkins')
    
    if STAGING_KEY_FILE_LOCAL_LOCATION:
        put(STAGING_KEY_FILE_LOCAL_LOCATION, use_sudo=True)
        with settings(warn_only=True):
            sudo('ssh -o "StrictHostKeyChecking no" %s' % STAGING_HOST, user='jenkins')
    
    if PRODUCTION_KEY_FILE_LOCAL_LOCATION:
        put(PRODUCTION_KEY_FILE_LOCAL_LOCATION, use_sudo=True)
        with settings(warn_only=True):
            sudo('ssh -o "StrictHostKeyChecking no" %s' % PRODUCTION_HOST, user='jenkins')
    
def setup_jenkins_server():
    """
    Sets up the ci environment
    
    """
    ci()
    
    install_jenkins()
    install_git()
    install_nginx()
    install_virtualenvwrapper()
    install_postgres()
    install_additional_packages()
    
    upload_ci_nginx_settings()
    setup_database_from_settings(CI_SETTINGS_PATH, test=True)
    add_pub_key()
    upload_env_keys()
    nginx('restart')
