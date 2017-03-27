import os

from celery import Celery

app = Celery('github_hooks',
             broker=os.environ.get('CELERY_BROKER_URL', 'redis://'),
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))


@app.task()
def push(json):
    print(json)


@app.task()
def create(json):
    print(json)


@app.task()
def ping(json):
    print(json)


@app.task()
def pull_request(json):
    print(json)


if __name__ == '__main__':
    app.worker_main()
