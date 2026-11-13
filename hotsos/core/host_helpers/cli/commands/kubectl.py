import glob
import json
import os
from collections import UserList

from hotsos.core.config import HotSOSConfig
from hotsos.core.host_helpers.cli.common import BinCmd, CmdOutput, FileCmd
from hotsos.core.host_helpers.exceptions import SourceNotFound
from hotsos.core.log import log

KUBECTL_ALIASES = ['kubectl', 'microk8s.kubectl', 'k8s kubectl']

# Paths checked by sos report
KUBE_CONFIGS = ['/etc/kubernetes/admin.conf',
                '/root/cdk/cdk_addons_kubectl_config',
                '/var/snap/microk8s/current/credentials/client.config']

# See https://kubernetes.io/docs/reference/kubectl/generated/kubectl_config for
# info on standard config paths.
#
# NOTE: the user can optionally set KUBECONFIG env var to override these paths.
DEFAULT_CFG_PATH = f"{os.environ.get('HOME', '~')}/.kube/config"


class KubectlBinCmdBase(BinCmd):
    """ Generic kubectl implementation for binary kubectl commands.

    Aims to support all kubectl commands and their subcommands in a format
    comparable to sosreport. This means that if e.g. sosreport executes the
    command with -o json then we need to do the same here for the binary
    version.
    """
    KUBECTL_CMD = None
    # If True the command is run against all namespaces rather than a
    # specific one and the namespace argument is not required.
    ALL_NAMESPACES = False

    @property
    def _use_json_encoding(self):
        return self.KUBECTL_CMD == 'get'

    def __init__(self, cmd, *args, **kwargs):
        if self.ALL_NAMESPACES:
            nsopt = '--all-namespaces'
        else:
            nsopt = '--namespace {namespace}'

        cmd = f'{cmd} {self.KUBECTL_CMD} {nsopt} {{opt}} {{subopts}}'

        # NOTE: sosreport runs kubectl get with -o json so we will do the
        # same for binary commands so that the api calls can be expect
        # consistent return type.
        if self._use_json_encoding:
            kwargs['json_decode'] = True

        super().__init__(cmd, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self._use_json_encoding:
            _subopts = kwargs.get('subopts', "")
            if not _subopts:
                kwargs['subopts'] = "-o json"
            else:
                kwargs['subopts'] += " -o json"

        return super().__call__(*args, **kwargs)


class KubectlLogsBinCmd(KubectlBinCmdBase):
    """ Implements kubectl logs binary command. """
    KUBECTL_CMD = 'logs'


class KubectlFileBinCmd(FileCmd):
    """ Implements kubectl logs file command. """
    KUBECTL_CMD = 'logs'

    def __call__(self, *args, **kwargs):
        subopts = kwargs.get('subopts')
        if subopts:
            kwargs['subopts'] = subopts.replace(' ', '_')

        return super().__call__(*args, **kwargs)


class KubectlLogsCmds(UserList):
    """ Generate kubectl logs command variants. """

    def __init__(self):
        cmds = [KubectlLogsBinCmd(cmd) for cmd in KUBECTL_ALIASES]

        confs = [p.replace('/', '.') for p in KUBE_CONFIGS]
        paths = []
        for cmd in KUBECTL_ALIASES:
            cmd = cmd.replace('.', '_').replace(' ', '_')
            paths.append('sos_commands/kubernetes/cluster-info/{namespace}/'
                         'podlogs/{opt}/' + cmd +
                         '_--namespace_{namespace}_logs_{opt}_{subopts}')

            paths.extend([(f'sos_commands/kubernetes/pods/{cmd}'
                           f'_--kubeconfig_{conf}'
                           '_--namespace_{namespace}_logs_{opt}'
                           '_{subopts}') for conf in
                          confs])

        for path in paths:
            cmds.append(KubectlFileBinCmd(path))

        super().__init__(cmds)


class KubectlGetBinCmd(KubectlBinCmdBase):
    """ Implements kubectl get """
    KUBECTL_CMD = 'get'


class KubectlGetCmds(UserList):
    """ Generate kubectl get command variants. """

    def __init__(self):
        cmds = [KubectlGetBinCmd(cmd) for cmd in KUBECTL_ALIASES]

        confs = [p.replace('/', '.') for p in KUBE_CONFIGS]
        paths = []
        for cmd in KUBECTL_ALIASES:
            cmd = cmd.replace('.', '_').replace(' ', '_')
            paths.extend([(f'sos_commands/kubernetes/{{opt}}/{cmd}'
                           f'_--kubeconfig_{conf}'
                           '_get_-o_json_--namespace_{namespace}_{opt}')
                          for conf in confs])

            paths.append('sos_commands/kubernetes/cluster-info/{namespace}/'
                         + cmd +
                         '_get_-o_json_--namespace_{namespace}_{opt}')

        for path in paths:
            cmds.append(FileCmd(path, json_decode=True))

        super().__init__(cmds)


class KubectlGetAllNamespacesBinCmd(KubectlGetBinCmd):
    """ Implements kubectl get --all-namespaces """
    ALL_NAMESPACES = True


class KubectlGetAllNamespacesFileCmd(FileCmd):
    """ Implements kubectl get --all-namespaces for sosreports.

    Sosreport does not save the output of kubectl get with --all-namespaces in
    json format (nor the output of kubectl get namespaces) but rather saves
    the json output of kubectl get for each namespace. Here we find all
    per-namespace outputs for a given resource type by matching any namespace
    in the path and merge their items into a single list so that the result
    has the same format as the binary command output.

    The path is expected to contain a {opt} field for the resource type and
    to use * in place of the namespace.
    """

    def __init__(self, *args, **kwargs):
        kwargs['json_decode'] = True
        super().__init__(*args, **kwargs)

    def __call__(self, *args, skip_load_contents=False, **kwargs):
        if args:
            self.path = self.path.format(*args)

        if kwargs:
            self.path = self.path.format(**kwargs)

        relpath = os.path.relpath(self.path, HotSOSConfig.data_root)
        pattern = os.path.join(glob.escape(HotSOSConfig.data_root), relpath)
        paths = sorted(glob.glob(pattern))
        self.reset()
        if not paths:
            raise SourceNotFound(pattern)

        items = []
        for path in paths:
            try:
                with open(path, encoding='utf-8') as fd:
                    items.extend(json.load(fd).get('items', []))
            except (OSError, json.JSONDecodeError, AttributeError):
                log.warning("failed to load kubectl output from %s", path)

        # NOTE: the output is a merge of multiple files so there is no single
        #       source path.
        return CmdOutput({'apiVersion': 'v1', 'kind': 'List',
                          'items': items, 'metadata': {}})


class KubectlGetAllNamespacesCmds(UserList):
    """ Generate kubectl get --all-namespaces command variants. """

    def __init__(self):
        cmds = [KubectlGetAllNamespacesBinCmd(cmd)
                for cmd in KUBECTL_ALIASES]

        confs = [p.replace('/', '.') for p in KUBE_CONFIGS]
        paths = []
        for cmd in KUBECTL_ALIASES:
            cmd = cmd.replace('.', '_').replace(' ', '_')
            prefixes = [cmd] + [f'{cmd}_--kubeconfig_{conf}'
                                for conf in confs]
            for prefix in prefixes:
                fname = f'{prefix}_get_-o_json_--namespace_*_{{opt}}'
                paths.append(f'sos_commands/kubernetes/{{opt}}/{fname}')
                paths.append(f'sos_commands/kubernetes/cluster-info/*/{fname}')

        for path in paths:
            cmds.append(KubectlGetAllNamespacesFileCmd(path))

        super().__init__(cmds)
