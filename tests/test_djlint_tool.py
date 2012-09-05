import unittest
import mock
from alfred_worker.tools import run_djlint
from djlint.analyzers.base import Result


def create_result(**kwargs):
    source = kwargs.pop('source', ())
    solution = kwargs.pop('solution', ())
    result = Result(**kwargs)
    for line in source:
        result.source.add_line(*line)
    for line in solution:
        result.solution.add_line(*line)
    return result


results = (
    create_result(
        description='description 1',
        path='path/to/file1.py',
        line=10,
        source=((10, 'source 1'),),
        solution=((10, 'solution 1'),),
    ),
    create_result(
        description='description 2',
        path='path/to/file2.py',
        line=20,
        source=((20, 'source 2'),),
        solution=((20, 'solution 2'),),
    ),
)

class DjLintTests(unittest.TestCase):

    @mock.patch('djlint.analyze', return_value=results)
    def test_iterates_by_djlint_results(self, analyze):
        fixes = list(run_djlint('path/to/repo'))
        analyze.assert_called_once_with('path/to/repo')
        self.assertEqual(fixes, [
            {
                'description': 'description 1',
                'path': 'path/to/file1.py',
                'line': 10,
                'source': [(10, True, 'source 1')],
                'solution': [(10, True, 'solution 1')],
            },
            {
                'description': 'description 2',
                'path': 'path/to/file2.py',
                'line': 20,
                'source': [(20, True, 'source 2')],
                'solution': [(20, True, 'solution 2')],
            },
        ])
