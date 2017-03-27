import os

from celery import Celery

url = os.environ.get('CELERY_BROKER_URL', 'redis://')
app = Celery('github_hooks',
             broker=url,
             backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis'))
app.conf.result_backend = url

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
