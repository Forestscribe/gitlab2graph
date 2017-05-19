import logging
import os
import sys
import unittest

import gitlab2graph

s = gitlab2graph.GLSession(os.environ['GITLAB_SERVER'], os.environ['GITLAB_TOKEN'])
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


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
    assert isinstance(ret['id'], int)
    assert len(ret['modules']) >= 1
    # assert ret['modules'][0]['submodule_git_url'].startswith("git@")
    # assert ret['modules'][0]['git_url'].startswith("https://github")
    # assert ret['modules'][0]['id'] == "forestscribetest/test_repo2"
    assert isinstance(ret['modules'][0]['id'], int)


def test_get_repo_info_nomodule():
    ret = s.getRepoInfos("forestscribetest", "test_repo3")
    assert ret['name'] == "test_repo3"
    assert ret['user'] == "forestscribetest"
    assert isinstance(ret['id'], int)


def test_getSubModuleDetails_outside():
    ret = s.getSubModuleDetails("forestscribe-android", "a_bsp_platform_external_pystache",
                                "/ext/spec", "http://github.com/mustache/spec.git")
    assert ret['id'] is not None


def test_get_repo_info_outside():
    ret = s.getRepoInfos("forestscribe-android", "a_bsp_platform_external_pystache")
    assert ret['name'] == "a_bsp_platform_external_pystache"
    assert ret['user'] == "forestscribe-android"
    assert not isinstance(ret['modules'][0]['id'], int)

def test_get_project_id():
    ret = s.getProjectIdFromUrl('git@github.forestscribe.intel.com:forestscribe-android/a_bsp_vendor_intel_apps_ituxd.git')
    assert isinstance(ret, int)
    ret2 = s.getProjectIdFromUrl('http://forestscribe.intel.com/forestscribe-android/a_bsp_vendor_intel_apps_ituxd')
    assert ret == ret2
