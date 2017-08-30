import json

import curio

from youtube_dl.postprocessor.common import PostProcessor

YTDL_OPTS = {
    'format': 'best',
    'progress_hooks': [],
    'quiet': True,
    'no_warnings': True,
    # 'simulate': True
}


class SortingPP(PostProcessor):
    pass


def format_percent(percent):
    if percent is None:
        return '---.-%'
    return f'{percent: >6.1%}'


async def read_json(path):
    """Attempt to read a JSON file. Returns False on error.
    :param path: the path of the file to read
    :return: the loaded JSON
    """
    try:
        async with curio.aopen(path, 'r') as f:
            data = await f.read()
            return json.loads(data)
    except IOError:
        return False


def write_json(to_write, path):
    """Write a serializable object to a JSON file.
    :param to_write: the object to write out
    :param path: the path of the file to output
    """
    with open(path, 'w') as f:
        json.dump(to_write, f, indent=2, sort_keys=True)


async def write_json_async(to_write, path):
    async with curio.aopen(path, 'w') as f:
        data = json.dumps(to_write, indent=2, sort_keys=True)
        await f.write(data)
