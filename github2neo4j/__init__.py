import os
from .github import GHSession
from .neo4j import Neo4jSession
__all__ = ['GHSession', 'Neo4jSession']


def dumpOneRepoToNeo4j(org, repo):
    gh = GHSession()
    n = Neo4jSession()
    n.insertGitHubModule(
        gh.getRepoInfos(org, repo))


def maybeCreateHook():
    gh = GHSession()
    res = gh.get("/user/orgs")
    res.raise_for_status()
    orgs = res.json()
    for org in orgs:
        org = org['login']
        gh.maybeCreateHook(org, os.environ["HOOKS_ROOT_URL"] + "/github")


def dumpAllReposToNeo4j():
    gh = GHSession()
    n = Neo4jSession()
    for org, repo in gh.getAllReposForUser():
        n.insertGitHubModule(
            gh.getRepoInfos(org, repo))
