import json
from os.path import dirname
from os.path import join


def load_data(filename, load_json=False):
    path = join(
        dirname(__file__),
        'data',
        filename
    )

    with open(path) as fh:
        if load_json:
            return json.loads(fh.read())
        else:
            return fh.read()
