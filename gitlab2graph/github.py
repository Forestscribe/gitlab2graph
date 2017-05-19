import configparser
import io
import os

from requests import Session

from .certs import install_intel_certs


class GHSession(Session):
    """a Session wrapper for github api"""
    def __init__(self):
        install_intel_certs()
        self.hosted_url = os.environ.get("HOOKS_GITHUB_URL")
        self.prefix_url = self.hosted_url + "/api/v3"
        super(GHSession, self).__init__()
        self.headers = {'Authorization': 'token ' + os.environ.get("HOOKS_GITHUB_TOKEN"),
                        'User-Agent': 'Github_hooks'}

    def request(self, method, url, *args, **kwargs):
        url = self.prefix_url + url
        res = super(GHSession, self).request(method, url, *args, **kwargs)
        return res

    def deleteAllHooks(self, org):
        """ delete all hooks (used for tests)"""
        res = self.get("/orgs/{org}/hooks".format(org=org))
        if res.status_code == 200:
            hooks = res.json()
            for hook in hooks:
                self.delete("/orgs/{org}/hooks/{id}".format(org=org, id=hook['id'])).raise_for_status()

    def maybeCreateHook(self, org, hook_url):
        """ enforce hook is created for hook_url

        returns True if it was created, False if it was already there
        """
        has_hook = False
        res = self.get("/orgs/{org}/hooks".format(org=org))
        if res.status_code == 200:
            hooks = res.json()
            for hook in hooks:
                if hook['config']['url'] == hook_url:
                    has_hook = True

        if not has_hook:
            res = self.post(
                "/orgs/{org}/hooks".format(org=org),
                json={
                    "name": "web",
                    "events": ["push", "pull_request"],
                    "config": {
                        "url": hook_url,
                        "content_type": "json"
                    }
                })
            res.raise_for_status()
        return not has_hook

    def getContent(self, org, repo, path, raw=False):
        headers = None
        if raw:
            headers = {"Accept": "application/vnd.github.VERSION.raw"}
        res = self.get("/repos/{org}/{repo}/contents/{path}".format(
            org=org, repo=repo, path=path), headers=headers)
        if res.status_code == 200:
            if raw:
                return res.content
            else:
                return res.json()
        return None

    def getSubModuleDetails(self, org, repo, path):
        res = self.get("/repos/{org}/{repo}/contents/{path}".format(
                       org=org, repo=repo, path=path))
        if res.status_code == 200:
            res = res.json()
            git_url = res['git_url']
            if git_url and git_url.startswith(self.hosted_url):
                res['id'] = "/".join(res['git_url'].split("/")[-5:-3])
            elif git_url is None:
                res['id'] = res['submodule_git_url']
            else:
                res['id'] = git_url

            return res

    def getRepoInfos(self, org, repo):
        bbtravis_yml = self.getContent(org, repo, ".bbtravis.yml", raw=True)
        gitmodules = self.getContent(org, repo, ".gitmodules", raw=True)
        modules = []
        if gitmodules is not None:
            config = configparser.ConfigParser()
            config.readfp(io.StringIO(gitmodules.replace(b"\t", b"").decode("utf8")))
            for section in config.sections():
                path = config.get(section, "path")
                res = self.getSubModuleDetails(org, repo, path)
                if res is not None:
                    modules.append(res)

        return dict(
            id=org + "/" + repo,
            user=org,
            name=repo,
            modules=modules,
            bbtravis_yml=bbtravis_yml
        )

    def getAllReposForOrg(self, org):
        """get all repo for one org, dealing with paging"""
        ret_repos = []
        page = 1
        while True:
            res = self.get("/orgs/{org}/repos".format(org=org), params=dict(page=page))
            if res.status_code != 200:
                break
            repos = res.json()
            if len(repos) == 0:
                break
            for repo in repos:
                ret_repos.append((org, repo['name']))

            page += 1
        return ret_repos

    def getAllReposForUser(self):
        res = self.get("/user/orgs")
        res.raise_for_status()
        repos = []
        orgs = res.json()
        for org in orgs:
            org = org['login']
            repos.extend(self.getAllReposForOrg(org))
        return repos
