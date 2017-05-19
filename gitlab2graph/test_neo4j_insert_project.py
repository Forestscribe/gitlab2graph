import os

import gitlab2graph

url = os.environ.get("NEO4J_URL")
auth = os.environ.get("NEO4J_CREDS").split(":")

s = gitlab2graph.Neo4jSession(url, auth)


def test_insertGitHubModule():
    s.insertGitHubModule({
        "name": "test_repo1",
        "user": "forestscribetest",
        "id": "forestscribetest/test_repo1",
        "bbtravis_yml": b"xx",
        "modules": [
            {"submodule_git_url": "git@xxx",
             "git_url": "https://github.com/forestscribetest/test_repo2",
             "id": "forestscribetest/test_repo2"
             }
        ]
    })
    s.insertGitHubModule({
        "name": "test_repo2",
        "user": "forestscribetest",
        "id": "forestscribetest/test_repo2",
        "bbtravis_yml": None,
        "modules": [
            {"submodule_git_url": "git@xxx",
             "git_url": "https://github.com/forestscribetest/test_repo3",
             "id": "forestscribetest/test_repo3"
             }
        ]
    })
    s.insertGitHubModule({
        "name": "test_repo3",
        "user": "forestscribetest",
        "id": "forestscribetest/test_repo3",
        "modules": [
        ]
    })
    res = s.findAllParentProjects("forestscribetest/test_repo3")
    assert sorted(res) == ["forestscribetest/test_repo1", "forestscribetest/test_repo2"]

    res = s.findAllParentProjects("forestscribetest/test_repo3", labels=["BBTravis"])
    assert sorted(res) == ["forestscribetest/test_repo1"]
