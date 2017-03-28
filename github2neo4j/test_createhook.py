import github2neo4j


def test_create_hook():
    s = github2neo4j.GHSession()
    hook_url = "http://localhost/"
    s.deleteAllHooks("forestscribetest")
    res = s.maybeCreateHook("forestscribetest", hook_url)
    assert res is True
    res = s.maybeCreateHook("forestscribetest", hook_url)
    assert res is False
    s.deleteAllHooks("forestscribetest")
