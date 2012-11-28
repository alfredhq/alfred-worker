import msgpack
import zmq
from .clone import clone


def run_worker(task, config):
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    for address in config['collectors']:
        socket.connect(address)

    push_id = task['push_id']
    try:
        for data in analyze(task, config.get('clones_root')):
            msg = msgpack.packb([push_id, 'fix', data])
            socket.send(msg)
    except Exception as e:
        error = str(e)
    else:
        error = None
    msg = msgpack.packb([push_id, 'finish', error])
    socket.send(msg)

    socket.close()
    context.term()


def analyze(task, clones_root):
    from .tools import tools

    owner_name = task['owner_name']
    repo_name = task['repo_name']
    hash = task['hash']
    with clone(owner_name, repo_name, hash, clones_root) as path:
        for tool in tools:
            for data in tool(path):
                yield data
