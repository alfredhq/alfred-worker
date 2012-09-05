import errno
import os
import shutil
import tempfile
from contextlib import contextmanager
from subprocess import Popen


GITHUB_TIMEOUT = 30
MAX_TARBALL_SIZE = 26214400


class CloneError(Exception):
    pass


@contextmanager
def tempdir(root=None):
    if root is not None:
        try:
            os.makedirs(root)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    path = tempfile.mkdtemp(dir=root)
    try:
        yield path
    finally:
        shutil.rmtree(path)


@contextmanager
def clone(owner_name, repo_name, hash, clones_root=None):
    with tempdir(root=clones_root) as path:
        tarball_path = _download_tarball(owner_name, repo_name, path, hash)
        repo_path = _extract_tarball(tarball_path)
        yield repo_path


def _get_tarball_url(owner_name, repo_name, hash):
    return 'https://github.com/%s/%s/tarball/%s' % (
        owner_name, repo_name, hash
    )


def _download_tarball(owner_name, repo_name, path, hash):
    tarball_url = _get_tarball_url(owner_name, repo_name, hash)
    tarball_path = os.path.join(path, 'archive.tar.gz')
    curl_string = 'curl %s --connect-timeout %d --max-filesize %d -L -s -o %s' % (
        tarball_url, GITHUB_TIMEOUT, MAX_TARBALL_SIZE, tarball_path
    )
    if Popen(curl_string.split()).wait():
        raise CloneError("Can't download tarball")
    return tarball_path


def _extract_tarball(tarball_path):
    repo_path = os.path.join(os.path.dirname(tarball_path), 'repo')
    os.makedirs(repo_path)
    if Popen(['tar', 'xf', tarball_path, '-C', repo_path]).wait():
        raise CloneError("Can't extract tarball")
    return repo_path
