import glob
import os

import git

from git.exc import GitCommandError
from gitdb.exc import BadName

from common import (
    constants,
    plugin_yaml,
)
from common.juju.juju_common import (
    JUJU_LIB_PATH,
)

class OpenstackCharmInfo(object):

    def __init__(self):
        self.info_cache = {}
        self.charm_source = {}
        self.source_dir = os.path.join(constants.PLUGIN_TMP_DIR,
                                       'charm_source')
        if not os.path.exists(self.source_dir):
            os.makedirs(self.source_dir) 

    def _get_charm_source(self, charm):
        if charm in self.charm_source:
            return

        git_url = os.path.join("https://opendev.org/openstack/charm-{}".format(
                               charm))
        dst = os.path.join(self.source_dir, "neutron-openvswitch")
        self.charm_source[charm] = git.Repo.clone_from(git_url, dst)

    def get_charm_release(self, charm):
        commit_id = None
        for path in glob.glob(os.path.exists(JUJU_LIB_PATH,
                              "agents/unit-{}-*".format(charm))):
            repo_info = os.path.join(path, "charm/repo-info")
            if os.path.exists(repo_info):
                commit_id = open(repo_info).read().strip()
                break

            r = self._get_charm_source(charm)
            r.checkout(commit_id)
