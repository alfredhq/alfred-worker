from setuptools import setup, find_packages


setup(
    name='alfred-worker',
    version='0.1.dev',
    license='ISC',
    description='Analyzes github repositories and detects code style issues',
    url='https://github.com/alfredhq/alfred-worker',
    author='Alfred Developers',
    author_email='team@alfredhq.com',
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=[
        'PyYAML',
        'msgpack-python',
        'pyzmq',

        'djlint',
    ],
    entry_points={
        'console_scripts': [
            'alfred-worker = alfred_worker.__main__:main',
        ],
    },
)
