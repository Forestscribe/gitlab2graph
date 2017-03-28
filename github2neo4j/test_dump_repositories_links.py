import github2neo4j

s = github2neo4j.GHSession()

def test_dump_repos():
    ret = s.getAllReposForOrg("forestscribetest")
    assert len(ret) >= 3


def test_get_content():
    ret = s.getContent("forestscribetest", "test_repo1", ".bbtravis.yml", True)
    assert b"language: python" in ret
    ret = s.getContent("forestscribetest", "test_repo1", ".bbtravis.yml_noexists", True)
    assert ret is None


def test_get_repo_info():
    ret = s.getRepoInfos("forestscribetest", "test_repo1")
    assert ret['name'] == "test_repo1"
    assert ret['user'] == "forestscribetest"
    assert len(ret['modules']) >= 1
    assert ret['modules'][0]['submodule_git_url'].startswith("git@")
    assert ret['modules'][0]['git_url'].startswith("https://github")
