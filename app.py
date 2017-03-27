from flask import Flask, request

from github_hooks import app as celery

app = Flask("github_hooks")


@app.route('/github', methods=['POST'])
def hook():
    event = request.headers.get('X-GitHub-Event')
    # we accept either form or json encoding
    json = request.json
    if json is None:
        json = request.form.to_dict(flat=True)
    celery.tasks['github_hooks.' + event].delay(json=json)
    return "OK"


@app.route('/', methods=['GET'])
def root():
    return "OK"
