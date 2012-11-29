import mock
import unittest
from alfred_worker.worker import analyze, clone, run_worker
from msgpack import packb


task = {
    'push_id': 1,
    'owner_name': 'alfredhq',
    'repo_name': 'alfred',
    'hash': 'ef45bc4e',
}

config = {
    'collectors': ['tcp://127.0.0.1:7000', 'tcp://127.0.0.1:7001'],
    'clones_root': 'clones/root',
}


class AnalyzeTests(unittest.TestCase):

    def setUp(self):

        self.tools = (
            mock.Mock(return_value=(mock.sentinel.fix1, mock.sentinel.fix2)),
            mock.Mock(return_value=(mock.sentinel.fix3, mock.sentinel.fix4)),
        )
        self.tools_patch = mock.patch('alfred_worker.tools.tools', self.tools)
        self.tools_patch.start()

        self.clone = mock.MagicMock(spec=clone)
        self.clone.return_value.__enter__.return_value = mock.sentinel.path
        self.clone_patch = mock.patch('alfred_worker.worker.clone', self.clone)
        self.clone_patch.start()

    def tearDown(self):
        self.tools_patch.stop()
        self.clone_patch.stop()

    def test_returns_fixes_from_all_tools(self):
        fixes = list(analyze(task, 'clones/root'))
        self.assertEqual(fixes, [
            mock.sentinel.fix1,
            mock.sentinel.fix2,
            mock.sentinel.fix3,
            mock.sentinel.fix4,
        ])

    def test_clones_task_repository(self):
        fixes = list(analyze(task, 'clones/root'))
        self.clone.assert_called_once_with(
            'alfredhq', 'alfred', 'ef45bc4e', 'clones/root'
        )

    def test_passes_cloned_repo_path_to_tools(self):
        fixes = list(analyze(task, 'clones/root'))
        self.tools[0].assert_called_once_with(mock.sentinel.path)
        self.tools[1].assert_called_once_with(mock.sentinel.path)


class RunWorkerTests(unittest.TestCase):

    def setUp(self):
        self.Context = mock.Mock()
        self.context = self.Context.return_value
        self.socket = self.context.socket.return_value
        self.context_patch = mock.patch('zmq.Context', self.Context)
        self.context_patch.start()

        self.fixes = (
            {'description': 'description 1'},
            {'description': 'description 2'},
        )
        self.analyze = mock.Mock(return_value=self.fixes)
        self.analyze_patch = mock.patch(
            'alfred_worker.worker.analyze', self.analyze
        )
        self.analyze_patch.start()

    def tearDown(self):
        self.context_patch.stop()
        self.analyze_patch.stop()

    def test_connects_to_collectors(self):
        run_worker(task, config)
        self.socket.connect.assert_has_calls([
            mock.call('tcp://127.0.0.1:7000'),
            mock.call('tcp://127.0.0.1:7001'),
        ])

    def test_sends_all_fixes_to_collectors(self):
        run_worker(task, config)
        self.socket.send.assert_has_calls([
            mock.call(packb([1, 'start', None])),
            mock.call(packb([1, 'fix', {'description': 'description 1'}])),
            mock.call(packb([1, 'fix', {'description': 'description 2'}])),
            mock.call(packb([1, 'finish', None]))
        ])

    def test_finishes_with_error_on_exception(self):
        self.analyze.side_effect = Exception('something is wrong')
        run_worker(task, config)
        self.socket.send.assert_has_calls([
            mock.call(packb([1, 'finish', 'something is wrong'])),
        ])
