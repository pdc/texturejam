# -*-coding: UTF-8 -*-
# Run these commands with fab

from fabric.api import local, settings, abort, run, cd, env, sudo, prefix
from fabric.contrib.console import confirm

env.hosts = ['texturejam@spreadsite.org']
env.site_name = 'texturejam'
env.virtualenv = env.site_name
env.settings_subdir = 'texturejam'
env.django_apps = ['api', 'recipes', 'hello']

def update_requirements():
    local("pip freeze | egrep -v 'Fabric|pycrypto|ssh' > REQUIREMENTS")

def test():
    with settings(warn_only=True):
        result = local('./manage.py test {0}'.format(' '.join(env.django_apps)), capture=True)
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

def push():
    local('git push')

def deploy():
    test()
    push()

    run('if [ ! -d static ]; then mkdir static; fi')
    run('if [ ! -d cache ]; then mkdir cache; fi')

    code_dir = '/home/{0}/Sites/{0}'.format(env.site_name)
    with cd(code_dir):
        run('git pull')
        run('cp {0}/settings_production.py {0}/settings.py'.format(env.settings_subdir))

        with prefix('. /home/{0}/virtualenvs/{1}/bin/activate'.format(env.site_name, env.virtualenv)):
            run('pip install -r REQUIREMENTS')
            run('pip install flup')
            run('./manage.py collectstatic --noinput')

    ##run('svc -du /service/{0}'.format(env.site_name))