import os

import github2neo4j
from celery import Celery
from celery.utils.log import get_task_logger

url = os.environ.get('CELERY_BROKER_URL', 'redis://')
app = Celery('github_hooks',
             broker=url,
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))
app.conf.result_backend = url
app.conf.acks_late = True


log = get_task_logger(__name__)


@app.task()
def ping(json):
    log.info('github ping {0}'.format(json))
    return


def do_event_generic(json):
    log.debug('handling {0}'.format(json))
    github2neo4j.dumpOneRepoToNeo4j(json.get('repository'))


@app.task()
def push(json):
    do_event_generic(json)


@app.task()
def create(json):
    do_event_generic(json)


@app.task()
def pull_request(json):
    do_event_generic(json)


@app.task()
def repository(json):
    do_event_generic(json)


@app.task()
def scan_all():
    log.info('scan all'.format())
    github2neo4j.maybeCreateHook()
    github2neo4j.dumpAllReposToNeo4j()


if __name__ == '__main__':
    app.worker_main()
