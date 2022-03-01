from core.plugintools import summary_entry_offset as idx
from core.plugins.kubernetes import KubernetesChecksBase

YAML_OFFSET = 0


class KubernetesSummary(KubernetesChecksBase):

    @idx(0)
    def __summary_services(self):
        return {'systemd': self.service_info,
                'ps': self.process_info}

    @idx(1)
    def __summary_snaps(self):
        snaps = self.snap_check.all_formatted
        if snaps:
            return snaps

    @idx(2)
    def __summary_dpkg(self):
        dpkg = self.apt_check.all_formatted
        if dpkg:
            return dpkg

    @idx(3)
    def __summary_pods(self):
        if self.pods:
            return self.pods

    @idx(4)
    def __summary_containers(self):
        if self.containers:
            return self.containers

    @idx(5)
    def __summary_flannel(self):
        info = {}
        for port in self.flannel_ports:
            info[port.name] = port.encap_info
            if port.addresses:
                info[port.name]['addr'] = port.addresses[0]

        if info:
            return info