from __future__ import absolute_import
import djlint


def run_djlint(path):
    for result in djlint.analyze(path):
        yield {
            'description': result.description,
            'path': result.path,
            'line': result.line,
            'source': list(result.source),
            'solution': list(result.solution),
        }
