Alfred Worker
=============

It:

- listens to coordinator for tasks;
- analyzes github repositories, associated with task, for code style issues;
- sends all issues to collectors.

Tasks from coordinator must be sent as dicts:

.. code:: python

    {
        'report_id': 1,
        'owner_name': 'alfredhq',
        'repo_name': 'alfred',
        'hash': '0680c2c0346672a89c145c8de095e2adda2766c8',
    }

You can run a worker using this command::

  $ alfred-worker config.yml

Config example:

.. code:: yaml

  num_workers: 4                            # number of CPUs will be used, if omitted
  clones_root: "/tmp/alfred-worker/clones"  # platform-dependent tempdir will be used, if omitted
  coordinator: "tcp://127.0.0.1:6000"
  collectors:
    - "tcp://127.0.0.1:7000"
    - "tcp://127.0.0.1:7001"
