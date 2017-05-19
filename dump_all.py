import logging
import sys

import click

from gitlab2graph import GLSession, Neo4jSession


@click.command()
@click.option('--kafka-server', envvar='KAFKA_SERVER', required=True)
@click.option('--gitlab-server', envvar='GITLAB_SERVER', required=True)
@click.option('--gitlab-token', envvar='GITLAB_TOKEN', required=True)
@click.option('--neo4j-server', envvar='NEO4J_URL', required=True)
@click.option('--neo4j-creds', envvar='NEO4J_CREDS', required=True)
@click.option('--debug/--no-debug', '-d', help='debug logging')
def process_events(kafka_server, gitlab_server, gitlab_token, neo4j_server, neo4j_creds, debug=False):
    """Simple program that shows last events from gitlab queue."""
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    gh = GLSession(gitlab_server, gitlab_token)
    n = Neo4jSession(neo4j_server, neo4j_creds.split(":"))
    for org, repo in gh.getAllReposForUser():
        n.insertGitHubModule(
            gh.getRepoInfos(org, repo))

if __name__ == '__main__':
    process_events()
