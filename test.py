import requests

requests.post('http://localhost:8000/github', headers={'X-GitHub-Event': 'push'}, json={'test': True})
