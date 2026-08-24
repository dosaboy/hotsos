=================
Shared properties
=================

NOTE: these properties can be used on their own or in conjunction with others e.g. :ref:`checks`.

Input
=====

Provides a common way to define input. Takes one or more filesystem paths or a
`CLIHelper command <https://github.com/canonical/hotsos/tree/main/hotsos/core/host_helpers/cli>`_.
When a command is provided, its output is written to a temporary file
and *input.path* is set to the path of that file.

This property is required by and used as input to the :ref:`search <search property>` property.

Usage:

.. code-block:: yaml

    input:
      command: hotsos.core.host_helpers.CLIHelper.<command>
      path: <path>
      options:
        disable-all-logs: <bool>
        args: [arg1]
        kwargs:
          key1: val1
        args-callback: import.path.to.method

The ``path`` and ``command`` settings are mutually exclusive. A path can be a
single filesystem path or a list of paths, all relative to :ref:`Data Root`.

PathFinder
----------

For applications that have more than one install method this can result in log
files existing in different locations. To support this, some plugins provide a
*PathFinder* which takes a relative log file path and returns the absolute path
if it exists based on one or more choice. To use a *PathFinder* do the
following:

.. code-block:: yaml

    input: '<plugin>:app.log'

Where "plugin" results in *hotsos.core.plugins.<name>.PathFinder* being
imported and called with *app.log* as a value. If the application uses either
of e.g. /var/log and /snap/app/common/log then both are checked until
one is found. This is useful so that we don't have to explicitly list all
possible paths for every search.

Logrotate Depth
---------------

By default, if ``--all-logs`` is provided to the hotsos client, it applies to
every path. Set ``options.disable-all-logs`` to ``true`` to disable this
behaviour for a specific input.

Using Command Output as Input
-----------------------------

To use command output as input, set ``command`` to a method name provided by
``CLIHelper``. The command is executed and its output is captured in a
temporary file.

If the command requires arguments, set ``options.args`` and
``options.kwargs`` to a list and dictionary respectively.

To generate command arguments dynamically, set ``options.args-callback`` to
the import path of an instance method. The method must take no arguments and
return a ``(list, dict)`` tuple containing positional and keyword arguments.

Cache keys:
* ``cmd_tmp_path`` - path to the temporary file containing command output.

Search property
===============

Used to define a search using expression(s) and constraints. Different types of
search expressions that can be used depending on the data being searched and how
the results will be interpreted:

**simple** search (`SearchDef <https://github.com/dosaboy/searchkit/tree/main/searchkit>`_) - a single pattern
used to match single lines.

**sequence** search (`SequenceSearchDef <https://github.com/dosaboy/searchkit/tree/main/searchkit>`_)  - used to match
(non-overlapping) sequences.

Search results are passed to their handler as a raw `SearchResultsCollection <https://github.com/dosaboy/searchkit/tree/main/searchkit>`_.

This property is implemented as a :ref:`mapped property <mappedproperties>` so the *search* name is optional.

IMPORTANT: do not use global search properties. If you do this, the same search
tag will be used for all searches and it will not be possible to
distinguish results from more than one leaf node.

Usage:

.. code-block:: yaml

    search:
      # the following are used to define a "simple" search
      expr: <str>
      hint: <str>
      # the following are used to define a "sequence" search
      start: <str>
      body: <str>
      end: <str>
      # If this is set to True it enables a passthrough sequence
      passthrough-results: True|False
      constraints:
        # Epoch (to current date i.e. CLIHelper.date()) that
        # results must fall within. Default is infinite.
        search-result-age-hours: <int>
        # Period of time within which we expect to find results.
        # Default is infinite.
        search-period-hours: <int>
        # Minimum number of search results required. If a search
        # period is defined, these must occur within that period.
        # Default is 1.
        min-results: <int>
        # Search result must be at least this number of hours
        # after the last boot time. Default is 0 (no limit).
        min-hours-since-last-boot: <int>

Search expressions can be a string or list of strings. Values beginning with
``$`` resolve a variable. Values beginning with ``@`` are treated as Python
property import paths. If an ``@`` import cannot be found, the value is used as
a literal expression.

To analyse logs containing overlapping sequences, perhaps from multiple
concurrent threads, set ``passthrough-results`` to ``true``. A passthrough
sequence requires both ``start`` and ``end`` expressions and is consumed by
the event-processing path.


Constraints are used to filter search results and are typically used in
conjunction with :ref:`checks`. In order to use constraints, search
expressions must match a timestamp using result group 1. The format of
timestamps e.g. in logs and command outputs will vary and there are handlers in
the code to support common formats.

Cache keys:

* simple_search - a *searchkit.SearchDef* object
* sequence_search - a *searchkit.SequenceSearchDef* object
* sequence_passthrough_search - a list of *searchkit.SearchDef* objects

The above keys are mostly used for internal purposes and the following extra
entries are added to provide a way to access search results in :ref:`raises`
(also see :ref:`PropertyCache`):

* ``search.results_group_<int>`` - values from capture group ``<int>`` across
  all results. Capture groups are numbered from 1.
* ``search.num_results`` - the number of results found by this search.
* ``search.files`` - the files containing one or more search results.

In the following example we demonstrate how to use these keys. A file called
*var/log/myapp.log* has contents:

.. code-block:: console

    2023-10-12 13:22:01 ERROR: queue 'small_queue' is full
    2023-10-12 14:12:33 ERROR: queue 'small_queue' is full

And we have a :ref:`scenario<scenarios overview>` like:

.. code-block:: yaml

    checks:
      errorsfound:
        input: var/log/myapp.log
        expr: '\S+ \S+ ERROR: queue ''(\S+)'' is full'
    conclusions:
      haserrors:
        decision: errorsfound
        raises:
          type: SomeWarning
          message: >-
            found {count} reports of queue full for queue(s): {queues}
          format-dict:
            count: '@checks.errorsfound.search.num_results'
            queues: '@checks.errorsfound.search.results_group_1:unique_comma_join'

The message string output would look like:

.. code-block:: console

    found 2 "queue full" error(s) for queue(s): small_queue

