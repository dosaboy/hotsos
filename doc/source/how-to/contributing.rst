Contribute to hotsos
====================

hotsos is an open source project that welcomes fixes, new analysis,
documentation improvements and other contributions.

Set up a development environment
--------------------------------

Fork and clone the `hotsos repository <https://github.com/canonical/hotsos>`_,
then create a virtual environment and install tox:

.. code-block:: console

    git clone https://github.com/<your-github-username>/hotsos.git
    cd hotsos
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip tox

The project supports Python 3.8 and later. Tox installs the dependencies needed
by each test environment.

Choose where to make a change
-----------------------------

hotsos is organised around plugins. A contribution normally touches one or
more of these areas:

``hotsos/defs``
    YAML definitions for scenario and event analysis. See :doc:`write-checks`
    for a guide to writing checks and :doc:`test-checks` for their YAML test
    format.

``hotsos/core``
    Shared Python code, including reusable plugin-specific helpers and the
    check engine.

``hotsos/plugin_extensions``
    Plugin output implementations. Each plugin contains classes derived from
    ``plugintools.PluginPartBase``. A ``summary`` property contributes at the
    plugin root, while a ``__summary_<key>`` property contributes beneath
    ``<plugin>.<key>``.

``tests/unit``
    Python unit tests and their fake data roots. Every code or analysis change
    should include focused test coverage.

Plugin output is collected into one summary and can be rendered as YAML, JSON,
Markdown or HTML. Do not print directly to standard output from library or
plugin code. Use the project logging helpers for diagnostic output and
``hotsos.core.issues`` to report detected issues.

Test a change
-------------

Run the unit tests for the code you changed first. A specific test can be run
by passing its test ID to the Python test environment:

.. code-block:: console

    tox -e py3 -- tests.unit.test_system.TestUbuntuPro.test_ubuntu_pro_attached

Before opening a pull request, run the complete default test suite:

.. code-block:: console

    tox

Useful focused environments include:

.. code-block:: console

    tox -e py3
    tox -e py3-coverage,coveragereport
    tox -e pep8
    tox -e pylint
    tox -e yamllint
    tox -e hotyvalidate
    tox -e docs

The coverage check requires at least 84 percent line and branch coverage.
Documentation changes must build without Sphinx warnings using ``tox -e docs``.

Submit a contribution
---------------------

Push your change to your fork and open a pull request against the ``main``
branch of the hotsos repository. In the pull request:

* Explain the problem and the approach taken.
* Include tests for changed behaviour, or explain why a test is not needed.
* Update the documentation when behaviour or user-facing interfaces change.
* Keep the change focused; use separate pull requests for unrelated work.

GitHub Actions runs the unit, coverage, lint, validation, functional and
documentation checks for every pull request. Address failures before requesting
review.