import os

import mock
import utils

from plugins.openstack.extras import get_extended_vm_info

FAKE_MASTER_YAML = os.path.join(utils.TESTS_DIR, "fake_master_yaml")
FAKE_YAML = """
openstack:
  instances:
"""


class TestOverlays(utils.BaseTestCase):

    def setUp(self):
        super().setUp()
        with open(FAKE_MASTER_YAML, 'w') as fd:
            fd.write(FAKE_YAML)

    def tearDown(self):
        super().tearDown()
        os.remove(FAKE_MASTER_YAML)

    @mock.patch.object(get_extended_vm_info, "VM_INFO", {"instances": {}})
    def test_get_node_instances(self):
        expected = {'instances': {
                        '09461f0b-297b-4ef5-9053-dd369c86b96b': {
                            'guest': 'instance-00000002',
                            'name': 'unknown',
                            'ports': ['fa:16:3e:02:20:bb']}
                        }
                    }
        os.environ["MASTER_YAML_OUT"] = FAKE_MASTER_YAML
        get_extended_vm_info.OpenstackExtendedInfo()()
        self.assertEquals(get_extended_vm_info.VM_INFO, expected)
