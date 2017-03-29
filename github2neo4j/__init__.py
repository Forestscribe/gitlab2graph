
from .github import GHSession
from .neo4j import Neo4jSession
__all__ = ['GHSession', 'Neo4jSession']


def DumpAllReposToNeo4j():
    gh = GHSession()
    n = Neo4jSession()
    for org, repo in gh.getAllReposForUser():
        n.insertGitHubModule(
            gh.getRepoInfos(org, repo))
