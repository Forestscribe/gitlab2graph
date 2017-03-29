import copy
import os

from neo4j.v1 import GraphDatabase, basic_auth


class Neo4jSession(object):
    def __init__(self):
        url = os.environ.get("NEO4J_URL")
        auth = os.environ.get("NEO4J_CREDS").split(":")
        self.driver = GraphDatabase.driver(url, auth=basic_auth(*auth))
        self.session = self.driver.session()

    def insertGitHubModule(self, module):
        _map = {}
        for k, v in module.items():
            if k != "modules":
                if isinstance(v, bytes):
                    v = v.decode("utf8")
                _map[k] = v
        labels = ""
        if "bbtravis_yml" in module and module['bbtravis_yml'] is not None:
            labels += ":BBTravis"
        if labels:
            labels = ", a" + labels
        with self.session.begin_transaction() as tx:
            tx.run("MERGE (a:GithubModule {id: {id}})"
                   " SET a = $map" + labels, {
                       "id": module['id'],
                       "map": _map
                   })
        for m in module['modules']:
            with self.session.begin_transaction() as tx:
                tx.run("MERGE (a:GithubModule {id: {child_id}})", {
                    "child_id": m['id']
                })
                tx.run(
                    "MATCH (a:GithubModule {id: {id}}), (b:GithubModule {id: {child_id}})"
                    "MERGE (a)-[r:GITMODULE_INCLUDES]->(b)", {
                        "id": module['id'],
                        "child_id": m['id']
                    })

    def findAllParentProjects(self, id, labels=None):
        if labels is None:
            labels = []
        labels = "".join([":" + x for x in labels])
        ret = []
        with self.session.begin_transaction() as tx:
            res = tx.run("MATCH (n:GithubModule" + labels + ")"
                         "-[:GITMODULE_INCLUDES *]->(m: GithubModule{id:{id}})"
                         " RETURN n.id", {"id": id})
            for i in res:
                ret.append(i['n.id'])
        return ret
