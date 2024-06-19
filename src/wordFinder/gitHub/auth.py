from github import Github
from github import Auth

from wordFinder import constants
from wordFinder import core


class GitHubGateway:
    """This is a context manager that allows to run the gitHub API functions."""
    def __init__(self, gitHubToken: str) -> None:
        """Initialisation of GitHubGateway.

        Parameters:
            gitHubToken: The GitHub personal access token to use to authenticate the user.
        """
        self.gitHubToken = gitHubToken
        self.gitHub = None

    def __enter__(self):
        """Authenticate the user and get his userName"""
        auth = Auth.Token(self.gitHubToken)
        self.gitHub = Github(auth=auth)
        self.gitUser = self.gitHub.get_user()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the GitHub session"""
        self.gitHub.close()


def gitHubRepositories():
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        return gitHubGateway.gitUser.get_repos()


def getRepoByName(repoName):
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        return gitHubGateway.gitUser.get_repos(repoName)


def branches(repoName):
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        repo = gitHubGateway.gitUser.get_repos(repoName)
        print(repo.get_branches())


def getContent(repoName, content):
    contentList = []
    with GitHubGateway(core.getConfigValueByName(constants.GIT_HUB_HEY)) as gitHubGateway:
        repo = gitHubGateway.gitUser.get_repos(repoName)
        for r in repo:
            if r.full_name == repoName:
                contents = r.get_contents("")
                while contents:
                    file_content = contents.pop(0)
                    if file_content.type == "dir":
                        contents.extend(r.get_contents(file_content.path))
                    else:
                        contentList.append(file_content)

    return contentList

