import unittest
import mock
import msgpack
from alfred_worker.__main__ import run
from alfred_worker.worker import run_worker


config = {
    'coordinator': 'tcp://127.0.0.1:6000',
}

tasks = (
    {
        'report_id': 1,
        'owner_name': 'alfredhq',
        'repo_name': 'alfred-db',
        'hash': 'dfe23abc',
    },
    {
        'report_id': 2,
        'owner_name': 'alfredhq',
        'repo_name': 'alfred',
        'hash': 'be23c3fa',
    },
)


class FakeSocket:

    def __init__(self):
        self.task_num = 0
        self.connect = mock.Mock()
        self.close = mock.Mock()

    def recv(self):
        try:
            task = tasks[self.task_num]
        except IndexError:
            raise KeyboardInterrupt
        self.task_num += 1
        return msgpack.packb(task)


class RunTests(unittest.TestCase):

    def setUp(self):
        self.Context = mock.Mock()
        self.context = self.Context.return_value
        self.context.socket.return_value = FakeSocket()
        self.context_patch = mock.patch('zmq.Context', self.Context)
        self.context_patch.start()

        self.Pool = mock.Mock()
        self.pool = self.Pool.return_value
        self.pool_patch = mock.patch('multiprocessing.Pool', self.Pool)
        self.pool_patch.start()

    def tearDown(self):
        self.context_patch.stop()
        self.pool_patch.stop()

    def test_sends_received_tasks_to_pool(self):
        run(config)
        self.pool.apply_async.assert_hash_calls([
            mock.call(run_worker, args=(tasks[0], config)),
            mock.call(run_worker, args=(tasks[1], config)),
        ])

    def test_closes_pool_properly_on_keyboardinterrupt(self):
        run(config)
        self.pool.terminate.assert_called_once_with()
