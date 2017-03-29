import unittest

import github2neo4j

s = github2neo4j.GHSession()


def test_dump_repos():
    ret = s.getAllReposForOrg("forestscribetest")
    assert len(ret) >= 3


@unittest.skip("test is too long")
def test_dump_repos_user():
    ret = s.getAllReposForUser()
    assert len(ret) >= 4


def test_get_content():
    ret = s.getContent("forestscribetest", "test_repo1", ".bbtravis.yml", True)
    assert b"language: python" in ret
    ret = s.getContent("forestscribetest", "test_repo1", ".bbtravis.yml_noexists", True)
    assert ret is None


def test_get_repo_info():
    ret = s.getRepoInfos("forestscribetest", "test_repo1")
    assert ret['name'] == "test_repo1"
    assert ret['user'] == "forestscribetest"
    assert ret['id'] == "forestscribetest/test_repo1"
    assert len(ret['modules']) >= 1
    assert ret['modules'][0]['submodule_git_url'].startswith("git@")
    assert ret['modules'][0]['git_url'].startswith("https://github")
    assert ret['modules'][0]['id'] == "forestscribetest/test_repo2"


def test_get_repo_info_nomodule():
    ret = s.getRepoInfos("forestscribetest", "test_repo3")
    assert ret['name'] == "test_repo3"
    assert ret['user'] == "forestscribetest"
    assert ret['id'] == "forestscribetest/test_repo3"


def test_getSubModuleDetails_outside():
    ret = s.getSubModuleDetails("forestscribe-android", "a_bsp_platform_external_pystache", "/ext/spec")
    assert ret['id'] is not None
