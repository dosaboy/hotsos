Architecture
============

hotsos is organised around *plugins* that provide easy access to the state of
applications and subsystems. The code that makes up hotsos is split into a few
distinct areas, described below.

Core library
------------

The implementation of plugins is split in two such that re-usable library code is kept in the `core plugin <https://github.com/canonical/hotsos/tree/main/hotsos/core/plugins>`_ code and everything else is treated as a `plugin extension <https://github.com/canonical/hotsos/tree/main/hotsos/plugin_extensions>`_.

For the full list of applications and subsystems covered, see
:doc:`../reference/plugins`.

Plugin extensions
-----------------

This is where the output summary is generated. It also provides a space to
extend core plugin functionality to generate additional output, for example
using :ref:`Events<events overview>`.

Defs
----

All scenario and event implementations.

Unit tests
----------

Python unit tests for all code.
