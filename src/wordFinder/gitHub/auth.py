from github import Github
from github import Auth

import constants
import core


class GitHubGateway:
    def __init__(self, gitHubToken):
        self.gitHubToken = gitHubToken
        self.gitHub = None

    def __enter__(self):
        auth = Auth.Token(self.gitHubToken)
        self.gitHub = Github(auth=auth)
        self.gitUser = self.gitHub.get_user()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.gitHub.close()


def gitHubRepositories():
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        return gitHubGateway.gitUser.get_repos()


def branches(repoName):
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        repo = gitHubGateway.gitUser.get_repos(repoName)
        print(repo.get_branches())
