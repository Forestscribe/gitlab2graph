import base64
import configparser
import io
import urllib

from requests import Session

from .certs import install_intel_certs


class GLSession(Session):
    """a Session wrapper for gitlab api"""
    def __init__(self, url, token):
        install_intel_certs()
        self._project_ids = {}
        url = url.rstrip("/")
        self.hosted_url = url
        self.prefix_url = self.hosted_url + "/api/v4"
        super(GLSession, self).__init__()
        self.headers = {'PRIVATE-TOKEN': token,
                        'User-Agent': 'Gitlab_hooks'}

    def request(self, method, url, *args, **kwargs):
        url = self.prefix_url + url
        res = super(GLSession, self).request(method, url, *args, **kwargs)
        return res

    def createGroup(self, org):
        for group in self.get("/groups", params=dict(search=org)).json():
            if group['path'] == org:
                return group
        r = self.post("/groups", json=dict(
            path=org,
            name=org,
            public=True
        ))
        return r.json()

    def createRepo(self, org, repo):
        r = self.post("/projects", json=dict(
            name=repo,
            namespace_id=org
        ))
        return r.json()

    def getProjectId(self, org, repo):
        path = urllib.parse.quote_plus(org + "/" + repo)
        if path not in self._project_ids:
            r = self.get("/projects/{org}%2F{repo}".format(
                org=org, repo=repo))
            r.raise_for_status()
            self._project_ids[path] = r.json()['id']
        return self._project_ids[path]

    def getProjectIdFromUrl(self, url):
        orig = url
        if url.endswith(".git"):
            url = url[:-4]
        url = url.split(":")[-1].split("/")[-2:]
        try:
            return self.getProjectId(*url)
        except Exception:
            return orig

    def getContent(self, org, repo, path, raw=False, ref="master"):
        path = urllib.parse.quote_plus(path)

        project_id = self.getProjectId(org, repo)
        # if raw:  # this endpoint does not work: https://gitlab.com/gitlab-org/gitlab-ce/issues/31470
        #     path += "/raw"

        res = self.get("/projects/{project_id}/repository/files/{path}".format(
            project_id=project_id, path=path), params=dict(ref=ref))
        if res.status_code == 200:
            j = res.json()
            if raw:
                return base64.b64decode(j['content'])
            else:
                return j
        return None

    def getSubModuleDetails(self, org, repo, path, url=None, ref="master"):
        path = urllib.parse.quote_plus(path)
        project_id = self.getProjectId(org, repo)
        res = self.get("/projects/{project_id}/repository/files/{path}".format(
            project_id=project_id, path=path), params=dict(ref=ref))
        if res.status_code == 200:
            res = res.json()
            project_id = self.getProjectIdFromUrl(url)
            ret = dict(id=project_id, blob_id=res['blob_id'], file_path=res['file_path'], url=url)
            return ret

    def getRepoInfos(self, org, repo):
        bbtravis_yml = self.getContent(org, repo, ".bbtravis.yml", raw=True)
        gitmodules = self.getContent(org, repo, ".gitmodules", raw=True)
        modules = []
        if gitmodules is not None:
            config = configparser.ConfigParser()
            config.readfp(io.StringIO(gitmodules.replace(b"\t", b"").decode("utf8")))
            for section in config.sections():
                path = config.get(section, "path")
                url = config.get(section, "url")
                res = self.getSubModuleDetails(org, repo, path, url)
                if res is not None:
                    modules.append(res)

        return dict(
            id=self.getProjectId(org, repo),
            user=org,
            name=repo,
            modules=modules,
            bbtravis_yml=bbtravis_yml
        )

    def getAllReposForOrg(self, org):
        """get all repo for one org, dealing with paging"""
        ret_repos = []
        page = 1
        if not isinstance(org, int):
            org = urllib.parse.quote_plus(org)
        while True:
            res = self.get("/groups/{org}/projects".format(org=org), params=dict(per_page=100, page=page))
            if res.status_code != 200:
                break
            repos = res.json()
            if len(repos) == 0:
                break
            for repo in repos:
                ret_repos.append((org, repo['path']))

            page += 1
        return ret_repos

    def getAllReposForUser(self):
        res = self.get("/groups")
        res.raise_for_status()
        repos = []
        orgs = res.json()
        for org in orgs:
            org = org['path']
            repos.extend(self.getAllReposForOrg(org))
        return repos
