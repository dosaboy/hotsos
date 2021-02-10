#!/usr/bin/python3
import glob
import gzip
import os
import re

import xml.etree.ElementTree as ET

from collections import OrderedDict

from common import cli_helpers, constants
from common.plugins.openstack import OpenstackChecksBase
from common import plugintools

NEUTRON_LOGPATH = os.path.join(constants.DATA_ROOT, "var/log/neutron")
VM_INFO = {"instances": {}}
guest_info = OrderedDict()
dhcp_allocations = {}


class OpenstackExtendedInfo(OpenstackChecksBase):

    def logsort(self, name):
        ret = re.compile(r".+\.log.?([0-9]*)(\.gz)?").match(name)
        if not ret or ret[1] == '':
            return 0

        return int(ret[1])

    def alloc_sort(self, alloc):
        ret = re.compile(r".+updated_at=([\S]+)Z,?.*").match(alloc)
        if not ret:
            return "0"

        return ret[1]

    def _get_allocations(self, fd, uuid, log):
        try:
            for line in fd.readlines():
                ret = re.compile(r".+reload_allocations.+device_id={}.+".
                                 format(uuid)).match(line)
                if not ret:
                    continue

                if uuid in dhcp_allocations:
                    dhcp_allocations[uuid].append(line)
                else:
                    dhcp_allocations[uuid] = [line]
        except Exception:
            print("ERROR: failed to parse dhcp info in {}".format(log))
        finally:
            fd.close()

    def get_instance_dhcp_allocations(self, logfiles, uuid):
        for log in logfiles:
            ret = re.compile(r".+\.log.+gz$").match(log)
            if ret:
                with gzip.open(log, 'rt') as fd:
                    self._get_allocations(fd, uuid, log)
            else:
                with open(log) as fd:
                    self._get_allocations(fd, uuid, log)

    def get_name(self, child):
        for _child in child:
            if _child.tag.endswith("name"):
                return _child.text
            else:
                val = self.get_name(_child)
                if val is not None:
                    return val

    def find_instance_by_uuid(self, uuid):
        for line in cli_helpers.CLIHelper().ps():
            ret = re.compile(r".+guest=(\S+),.+product=OpenStack Nova.+uuid={}"
                             r".+".format(uuid)).match(line)
            if ret:
                guest = ret[1]
                if guest not in guest_info:
                    guest_info[uuid] = {"name": "unknown",
                                        "guest": guest,
                                        "ports": []}

                ret = re.compile(r"mac=([a-z0-9:]+)").findall(line)
                if ret:
                    guest_info[uuid]["ports"] += ret

                path = os.path.join(constants.DATA_ROOT,
                                    "etc/libvirt/qemu/{}.xml".format(guest))
                if os.path.exists(path):
                    tree = ET.parse(path)
                    for child in tree.getroot():
                        if child.tag == "metadata":
                            guest_info[uuid]["name"] = self.get_name(child)
                            break

    def get_dhcp_allocation_info(self):
        logfiles = sorted(glob.glob(os.path.join(NEUTRON_LOGPATH,
                                                 "neutron-dhcp-agent.log*")),
                          key=self.logsort)
        for uuid in self.running_instances:
            self.get_instance_dhcp_allocations(logfiles, uuid)

        if not dhcp_allocations:
            return

        for uuid in dhcp_allocations:
            allocations = {}
            VM_INFO["instances"][uuid]["dhcp_allocations"] = allocations
            for i, allocation in enumerate(sorted(dhcp_allocations[uuid],
                                                  key=self.alloc_sort)):
                allocation = re.compile(r".+allocations for port (.+)"
                                        ).match(allocation)[1]

                allocations = {i: {}}
                for field in allocation.split(", "):
                    for key in ["binding:host_id",
                                "created_at",
                                "device_id",
                                "dns_name",
                                "mac_address",
                                "network_id",
                                "revision_number",
                                "updated_at"]:
                        ret = re.compile("{}=(.+)".format(key)).match(field)
                        if ret:
                            allocations[i][key] = ret[1]

    def get_node_instances(self):
        for uuid in self.running_instances:
            self.find_instance_by_uuid(uuid)

        for uuid in guest_info:
            VM_INFO["instances"][uuid] = {"ports": []}
            for key in guest_info[uuid]:
                if key == "ports":
                    for port in guest_info[uuid]["ports"]:
                        VM_INFO["instances"][uuid]["ports"].append(port)
                else:
                    VM_INFO["instances"][uuid][key] = guest_info[uuid][key]

    def __call__(self):
        self.get_node_instances()
        self.get_dhcp_allocation_info()


if __name__ == "__main__":
    OpenstackExtendedInfo()()
    if VM_INFO:
        plugintools.update_part(VM_INFO, "vm_info.py")
