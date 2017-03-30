import unittest

from github2neo4j import dumpAllReposToNeo4j


@unittest.skip("test is too long")
def test_DumpAllReposToNeo4j():
    dumpAllReposToNeo4j()
