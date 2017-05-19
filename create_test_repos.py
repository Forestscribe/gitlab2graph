import logging
import sys

import click

import gitlab2graph
from gitlab2graph.gitlab import GLSession


def do_event(event):
    project_id = event.get('project_id')
    if project_id:
        gitlab2graph.dumpOneRepoToNeo4j(project_id)


@click.command()
@click.option('--gitlab-server', envvar='GITLAB_SERVER', required=True)
@click.option('--gitlab-token', envvar='GITLAB_TOKEN', required=True)
@click.option('--debug/--no-debug', '-d', help='debug logging')
def process_events(gitlab_server, gitlab_token, debug=False):
    """Simple program that shows last events from gitlab queue."""
    global gitlab, hook_url
    gitlab = GLSession(gitlab_server, gitlab_token)
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    group = gitlab.createGroup("forestscribetest")['id']
    gitlab.createRepo(group, "test_repo1")
    gitlab.createRepo(group, "test_repo2")
    gitlab.createRepo(group, "test_repo3")

if __name__ == '__main__':
    process_events()
