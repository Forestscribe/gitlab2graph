import logging
import sys

import bson
import click
from kafka import KafkaConsumer

from gitlab2graph import GLSession, Neo4jSession


@click.command()
@click.option('--kafka-server', envvar='KAFKA_SERVER', required=True)
@click.option('--gitlab-server', envvar='GITLAB_SERVER', required=True)
@click.option('--gitlab-token', envvar='GITLAB_TOKEN', required=True)
@click.option('--debug/--no-debug', '-d', help='debug logging')
@click.option('--neo4j-server', envvar='NEO4J_URL', required=True)
@click.option('--neo4j-creds', envvar='NEO4J_CREDS', required=True)
def process_events(kafka_server, gitlab_server, gitlab_token, neo4j_server, neo4j_creds, debug=False):

    gitlab = GLSession(gitlab_server, gitlab_token)
    n = Neo4jSession(neo4j_server, neo4j_creds.split(":"))
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    consumer = KafkaConsumer('gitlabbson', group_id="gitlab2graph", fetch_max_wait_ms=10000,
                             bootstrap_servers=[kafka_server])
    for event in consumer:
        event = bson.loads(event.value)
        print (event)
        if event.get('object_kind') in ('push', 'tag_push'):
            org, repo = event['project']['path_with_namespace'].rsplit("/", 1)
            n.insertGitHubModule(
                gitlab.getRepoInfos(org, repo))
            print("updated", org, repo)

if __name__ == '__main__':
    process_events()
