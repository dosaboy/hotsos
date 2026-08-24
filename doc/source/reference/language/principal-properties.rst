====================
Principal properties
====================

These are the principal properties used to build :doc:`../../explanation/scenarios`
and other analysis. They are typically combined with the
:doc:`shared-properties` and :doc:`requirement-types`.

Vars
====

Use the ``vars`` property to define one or more variables that can be referenced
from other properties. Variables are defined as a mapping of ``key: value``
pairs. Values can be standard YAML types such as strings, integers and booleans:

.. code-block:: yaml

  vars:
    sfoo: foo
    ifoo: 400
    bfoo: true

They can also reference a Python property. Prefix the import path with ``@``:

.. code-block:: yaml

  vars:
    foo: '@path.to.myproperty'

A :ref:`factory <FactoryClasses>` reference can use the following form:

.. code-block:: yaml

  vars:
    foo: '@<modpath>.<factoryclassname>.<property>:<input>'

The property is resolved lazily when ``$foo`` is used.

Accessing
---------

Access a variable from another property by prefixing its name with ``$``:

.. code-block:: yaml

  vars:
    foo: true
  checks:
    foo_is_true:
      requires:
        varops: [[$foo], [eq, true]]

Variables are accessible from any property within the file in which they are defined.

NOTE: global properties are not yet supported.

Checks
======

A dictionary of labelled checks, each of which groups one or more properties.
Each check is executed independently and produces a boolean result. Multiple
properties within a check are combined with logical AND by default; explicit
:ref:`LogicalGroupings` are also supported.

Checks are normally implemented in conjunction with :ref:`Conclusions<conclusions>`
as part of :ref:`Scenarios<scenarios overview>`.

Usage:

.. code-block:: yaml

    checks:
      error_found:
        input: var/log/myapp.log
        search:
          expr: 'ERROR: .+'
      service_ready:
        systemd:
          myapp: active


The following properties are supported:

* :ref:`Input<input>`
* :ref:`Requires<requires>`
* :ref:`Search<search property>`

Cache keys:

* ``search`` - the search property cache, when the check contains a search.
  It contains ``num_results`` and ``files``. The latter lists files that
  contain matches, rather than every file searched.
* ``requires`` - the requires property cache, when the check contains a
  requirement.

Conclusions
===========

A conclusion is used in :ref:`Scenarios <scenarios overview>` to derive an
outcome from one or more :ref:`checks <checks>`. When a conclusion is matched,
it raises a bug or issue with a message describing the identified problem and,
where appropriate, suggested actions. Conclusions have priority 1 by default;
set ``priority`` to an integer to override it. Conclusions with the highest
priority take precedence.

The message can optionally use format fields which, if used, require
format-dict to be provided with key/value pairs. The values must be
an importable attribute, property or method.

Usage:

.. code-block:: yaml

    conclusions:
      <name>:
        priority: <int>
        decision: <check name or logical grouping>
        raises:
          type: <issue class name>
          message: <format string>
          format-dict:
            <key>: <value>


The following provides an explanation of the fields required to define a conclusion:

Decision
--------

This property is used in :ref:`Conclusions<conclusions>`. Its value can be one
check name, a list of check names (implicit AND), or check names organised with
:ref:`LogicalGroupings`. Supported group operators include ``and``, ``or``,
``not`` and ``nor``.

Usage:

.. code-block:: yaml

    decision: check1

  or:

  .. code-block:: yaml

    decision: [check1, check2]

  or:

  .. code-block:: yaml

    decision:
      or:
      - check1
      - and: [check2, check3]

Priority
--------

Defines an integer priority. This is a very simple property that is typically
used by :ref:`conclusions` to associate a priority or precedence to
conclusions.

Usage:

.. code-block:: yaml

    priority: <int>

Raises
------

Defines an issue to raise and the message to display. ``type`` is the class name
of an issue exported by ``hotsos.core.issues``, not a Python import path. A
:ref:`Checks<checks>` result can be used to format the message with values from
Python properties, variables or property caches.

Usage:

.. code-block:: yaml

    raises:
      type: <type>
      bug-id: <str>
      cve-id: <str>
      message: <str>
      format-dict: <dict>

If *type* is a `bug or cve type <https://github.com/canonical/hotsos/blob/main/hotsos/core/issues/issue_types.py>`_ then a
*bug-id* or *cve-id* must be provided respectively.

If ``message`` contains format fields, fill them with ``format-dict``. Each key
must match a field in the message. A value can be a Python import path, a
``$variable`` reference or a
:ref:`property cache reference <PropertyCache>`. References can be suffixed
with a supported renderer, for example ``:first`` or ``:unique_comma_join``.

Requires
========

Defines one or more :ref:`requirements <requirement types>` that produce a
pass/fail result. Within a check, ``requires`` is a
:ref:`mapped property <mappedproperties>`, so its name can be omitted. For
example, these definitions are equivalent:

.. code-block:: yaml

    checks:
      explicit:
        requires:
          systemd:
            ufw: active
      implicit:
        systemd:
          ufw: active

Usage:

The simplest form contains a single type e.g.:

.. code-block:: yaml

    requires:
      systemd:
        ufw: active
        
This requirement stipulates that a systemd service called ufw must exist and have state active for the result to be True.

A requirement can also contain a collection of types grouped as a :ref:`LogicalGroupings` e.g.

.. code-block:: yaml

    requires:
      or:
        - apt: ufw
        - snap: ufw
      systemd:
        ufw: active

This requires the ufw package be installed as a snap or apt package and the corresponding systemd service be in active state.

Note that if more than one item in a group has the same type, a list must used e.g.

.. code-block:: yaml

    requires:
      and:
        - systemd:
            ufw: active
        - systemd:
            ssh: active

The final result of a list, or of multiple ungrouped requirements, is obtained
by applying AND to all results.

Requirement types that support ``ops`` accept a list of operations applied in
sequence. Each operation is a one- or two-item list containing a function name
from Python's `operator module <https://docs.python.org/3/library/operator.html>`_
and, when required, its second argument. Each operation receives the output of
the previous operation. See :ref:`property requirement` and
:ref:`varops requirement` for examples.

For supported "requirement type" properties see :ref:`requirement types`
