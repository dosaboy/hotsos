import os
from unittest import mock

from hotsos.core.config import HotSOSConfig
from hotsos.core import host_helpers
from hotsos.core.plugins import kubernetes
from hotsos.plugin_extensions.kubernetes import summary

from . import utils

SNAP_LIST_ALL_NO_K8S = """
Name                     Version    Rev    Tracking       Publisher   Notes
lxd                      4.0.8      21835  4.0/stable/…   canonical*  -
snapd                    2.54.2     14549  latest/stable  canonical*  snapd
"""

SNAP_LIST_ALL_MICROK8S = """
Name      Version        Rev    Tracking       Publisher    Notes
core18    20230320       2721   latest/stable  canonical*   base
core20    20230308       1852   latest/stable  canonical*   base
core22    20230404       617    latest/stable  canonical*   base
hotsos    1.1.13.post32  707    latest/stable  hopem        classic
lxd       5.0.2-838e1b2  24322  5.0/stable/…   canonical*   -
microk8s  v1.26.4        5219   1.26/stable    canonical*   classic
nvim      v0.9.0         2801   latest/stable  neovim-snap  classic
snapd     2.59.1         18933  latest/stable  canonical*   snapd
"""


class KubernetesTestsBase(utils.BaseTestCase):
    """ Custom base testcase that sets kubernetes plugin context. """
    def setUp(self):
        super().setUp()
        HotSOSConfig.plugin_name = 'kubernetes'
        HotSOSConfig.data_root = os.path.join(utils.TESTS_DIR,
                                              'fake_data_root/kubernetes')


class TestKubernetesSummary(KubernetesTestsBase):
    """ Unit tests for kubernetes summary. """
    def test_services(self):
        """Test kubernetes services summary output."""
        expected = {'systemd': {
                        'enabled': [
                            'calico-node',
                            'containerd',
                            'flannel',
                            'kube-proxy-iptables-fix',
                            'snap.kube-apiserver.daemon',
                            'snap.kube-controller-manager.daemon',
                            'snap.kube-proxy.daemon',
                            'snap.kube-scheduler.daemon']},
                    'ps': [
                        'calico-node (3)',
                        'containerd (1)',
                        'containerd-shim-runc-v2 (1)',
                        'flanneld (1)',
                        'kube-apiserver (1)',
                        'kube-controller-manager (1)',
                        'kube-proxy (1)',
                        'kube-scheduler (1)']}
        inst = summary.KubernetesSummary()
        self.assertEqual(self.part_output_to_actual(inst.output)['services'],
                         expected)

    def test_snaps(self):
        """Test kubernetes snaps summary output."""
        result = ['cdk-addons 1.23.0 (latest/stable)',
                  'core 16-2.54.2 (latest/stable)',
                  'core18 20211215 (latest/stable)',
                  'core20 20220114 (latest/stable)',
                  'kube-apiserver 1.23.3 (latest/stable)',
                  'kube-controller-manager 1.23.3 (latest/stable)',
                  'kube-proxy 1.23.3 (latest/stable)',
                  'kube-scheduler 1.23.3 (latest/stable)',
                  'kubectl 1.23.3 (latest/stable)']
        inst = summary.KubernetesSummary()
        self.assertEqual(self.part_output_to_actual(inst.output)['snaps'],
                         result)

    @mock.patch.object(host_helpers.packaging, 'CLIHelper')
    def test_snaps_no_k8s(self, mock_helper):
        """Test summary is not runnable without k8s snaps."""
        mock_helper.return_value.snap_list_all.return_value = \
            SNAP_LIST_ALL_NO_K8S.splitlines()
        inst = summary.KubernetesSummary()
        self.assertFalse(inst.is_runnable())
        self.assertNotIn('snaps', inst.output)

    def test_network_info(self):
        """Test kubernetes flannel network info output."""
        expected = {'flannel.1': {'addr': '10.1.84.0',
                                  'vxlan': {'dev': 'ens3',
                                            'id': '1',
                                            'local_ip': '10.6.3.201'}}}
        inst = summary.KubernetesSummary()
        self.assertEqual(self.part_output_to_actual(inst.output)['flannel'],
                         expected)

    @mock.patch.object(host_helpers.packaging, 'CLIHelper')
    def test_snaps_microk8s(self, mock_helper):
        """Test summary with microk8s snap installed."""
        mock_helper.return_value.snap_list_all.return_value = \
            SNAP_LIST_ALL_MICROK8S.splitlines()
        inst = summary.KubernetesSummary()
        result = ['core18 20230320 (latest/stable)',
                  'core20 20230308 (latest/stable)',
                  'core22 20230404 (latest/stable)',
                  'microk8s v1.26.4 (1.26/stable)']
        self.assertTrue(inst.is_runnable())
        self.assertEqual(self.part_output_to_actual(inst.output)['snaps'],
                         result)


class TestKubernetesBase(KubernetesTestsBase):
    """ Unit tests for kubernetes base helpers. """
    def test_cluster_pods(self):
        """Test listing all pods in the cluster from a sosreport."""
        expected = {'default': ['ubuntu-debug-5c8d99cd56-dvcdv',
                                'ubuntu-debug-5c8d99cd56-jssfv'],
                    'ingress-nginx-kubernetes-worker':
                        ['default-http-backend-kubernetes-worker-'
                         '6cd58d8886-psxtt',
                         'nginx-ingress-controller-kubernetes-worker-kgczb',
                         'nginx-ingress-controller-kubernetes-worker-n8dls'],
                    'kube-system': ['calico-kube-controllers-5f885f6465-zpvgw',
                                    'coredns-5564855696-86vtt',
                                    'csi-cinder-controllerplugin-0',
                                    'csi-cinder-nodeplugin-bb9jk',
                                    'csi-cinder-nodeplugin-zcpxd',
                                    'k8s-keystone-auth-6fff776dcd-c97s9',
                                    'k8s-keystone-auth-6fff776dcd-ngft9',
                                    'kube-state-metrics-5ccbcf64d5-mvsq8',
                                    'metrics-server-v0.5.1-79b4746b65-vxlqh',
                                    'openstack-cloud-controller-manager-'
                                    'dx8br',
                                    'openstack-cloud-controller-manager-'
                                    'm58w4'],
                    'kubernetes-dashboard':
                        ['dashboard-metrics-scraper-5cd54464bf-t94lc',
                         'kubernetes-dashboard-55796c99c-gnvlw']}
        self.assertEqual(kubernetes.KubernetesBase().cluster_pods, expected)

    @mock.patch.object(kubernetes, 'CLIHelper')
    def test_cluster_pods_no_data(self, mock_helper):
        """Test listing cluster pods when kubectl returns nothing."""
        mock_helper.return_value.kubectl_get_all_namespaces.return_value = []
        self.assertEqual(kubernetes.KubernetesBase().cluster_pods, {})

    @mock.patch.object(kubernetes, 'CLIHelper')
    def test_cluster_pods_bad_items(self, mock_helper):
        """Test listing cluster pods skips items with missing metadata."""
        mock_helper.return_value.kubectl_get_all_namespaces.return_value = \
            {'items': [{'metadata': {'name': 'p1', 'namespace': 'ns1'}},
                       {'metadata': {'name': 'p2'}}]}
        self.assertEqual(kubernetes.KubernetesBase().cluster_pods,
                         {'ns1': ['p1']})


@utils.load_templated_tests('scenarios/kubernetes')
class TestKubernetesScenarios(KubernetesTestsBase):
    """
    Scenario tests can be written using YAML templates that are auto-loaded
    into this test runner. This is the recommended way to write tests for
    scenarios. It is however still possible to write the tests in Python if
    required. See https://hotsos.readthedocs.io/en/latest/contrib/testing.html
    for more information.
    """
