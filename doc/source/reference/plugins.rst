Supported plugins
==================

hotsos is organised around *plugins* that provide easy access to the state of
an application or subsystem. When run, hotsos executes every plugin, and each
one contributes a section to the summary. The following plugins cover common
cloud applications as well as core system areas:

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Plugin
     - Covers
   * - `juju <https://canonical.com/juju>`_
     - Juju models, applications and units.
   * - `kernel <https://ubuntu.com/kernel>`_
     - Kernel version, configuration and log analysis.
   * - `kubernetes <https://kubernetes.io/>`_
     - Kubernetes cluster components.
   * - `lxd <https://canonical.com/lxd>`_
     - LXD containers and configuration.
   * - `maas <https://maas.io/>`_
     - MAAS region and rack controllers.
   * - `microcloud <https://canonical.com/microcloud>`_
     - MicroCloud deployments.
   * - `mysql <https://dev.mysql.com/doc/refman/8.0/en/mysql-innodb-cluster-introduction.html>`_
     - MySQL and MySQL InnoDB Cluster.
   * - `openstack <https://www.openstack.org/>`_
     - OpenStack services.
   * - `openvswitch <https://www.openvswitch.org/>`_
     - Open vSwitch and `OVN <https://www.ovn.org/en/>`_.
   * - `rabbitmq <https://www.rabbitmq.com/>`_
     - RabbitMQ message broker.
   * - `sosreport <https://sos.readthedocs.io/en/main/>`_
     - The sosreport being analysed.
   * - storage
     - `Ceph <https://ceph.com/en/>`_ and
       `bcache <https://docs.kernel.org/admin-guide/bcache.html>`_.
   * - system
     - General host/system information.
   * - `vault <https://developer.hashicorp.com/vault>`_
     - HashiCorp Vault.

For a discussion of how plugins are implemented, see
:doc:`../explanation/architecture`.
