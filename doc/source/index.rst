:sd_hide_title:

hotsos
======

.. rst-class:: h1

Hotsos Documentation
====================

hotsos implements repeatable analysis to extract useful information from common
cloud applications and subsystems. It is run against a :ref:`data root` — either
the host it runs on or a `sosreport <https://github.com/sosreport/sos>`_ — and
produces a summary containing key information from each plugin along with any
issues or known bugs detected, together with suggestions on what actions can be
taken to handle them.

Analysis is written in a high-level YAML language backed by helpful Python
libraries, and hotsos ships with a catalog of ready-made analysis for
applications such as OpenStack, Ceph, Kubernetes, OVS/OVN, RabbitMQ and more.

.. grid:: 1 1 2 2
   :gutter: 3
   :margin: 0
   :padding: 0

   .. grid-item-card:: :octicon:`mortar-board;1.5em;sd-mr-1` Tutorial
      :link: tutorial/index
      :link-type: doc

      **Start here** — a hands-on introduction to hotsos for newcomers.
      Install the tool and run your first analysis.

   .. grid-item-card:: :octicon:`tools;1.5em;sd-mr-1` How-to guides
      :link: how-to/index
      :link-type: doc

      **Step-by-step guides** covering key operations such as installing
      hotsos, running an analysis and writing your own checks.

   .. grid-item-card:: :octicon:`book;1.5em;sd-mr-1` Reference
      :link: reference/index
      :link-type: doc

      **Technical information** — the analysis language, its properties and
      the plugins that hotsos supports.

   .. grid-item-card:: :octicon:`light-bulb;1.5em;sd-mr-1` Explanation
      :link: explanation/index
      :link-type: doc

      **Discussion and clarification** of how hotsos is built and the concepts
      behind scenarios, events and checks.

Project and community
---------------------

hotsos is an open source project that welcomes community contributions,
suggestions, fixes and constructive feedback.

* Get the source and raise issues on `GitHub <https://github.com/canonical/hotsos>`_
* Learn how to :doc:`contribute to hotsos <how-to/contributing>`
* Learn how to :doc:`write and test your own checks <how-to/write-checks>`

.. toctree::
   :hidden:
   :maxdepth: 2

   tutorial/index
   how-to/index
   reference/index
   explanation/index
