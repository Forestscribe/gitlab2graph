
from urllib import parse

from pydgraph.client import DgraphClient


class DGraphSession(object):
    def __init__(self, url):
        url = parse.urlparse(url)
        self.driver = DgraphClient.driver(url.hostname.split(":"))

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
            # delete all relation from this module first
            tx.run("MATCH (a:GithubModule {id: {id}})-[r:GITMODULE_INCLUDES]-()"
                   "DELETE r",
                   {"id": module['id']})

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
