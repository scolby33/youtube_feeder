import collections
import logging
import os
import re
import time

import asks
import curio
import feedparser
import opml
import youtube_dl

from .exceptions import CancellationRequestedError
from .gui import gui
from .util import YTDL_OPTS, format_percent, read_json, write_json

logger = logging.getLogger(__name__)


class DownloadProgressModel(object):
    def __init__(self):
        self._videos = collections.OrderedDict()
        self._requested_cancellations = set()

    def add_video(self, video_id, title, download_task):
        self._videos[video_id] = {
            'status': 'pending',
            'title': title,
            'task': download_task
        }

    def cancel_download(self, video_id):
        self._requested_cancellations.add(video_id)

    def cancel_all_downloads(self):
        self._requested_cancellations.update(self._videos.keys())

    def progress_hook(self, progress_info):
        video_id = self.video_id_from_filename(progress_info['filename'])
        if video_id in self._requested_cancellations:
            progress_info['status'] = 'cancelled'
            self._videos[video_id].update(progress_info)
            self._requested_cancellations.remove(video_id)
            raise CancellationRequestedError()
        self._videos[video_id].update(progress_info)

    def get_summary(self):
        return [
            (
                (meta.get('title', 'Unknown'), meta.get('_percent_str', ''), meta.get('status')[0]),
                video_id
            )
            for video_id, meta in self._videos.items()
        ]

    @staticmethod
    def video_id_from_filename(filename):
        return f'yt:video:{os.path.splitext(filename)[0][-11:]}'


def parse_subscriptions(subscriptions_data):
    outline = opml.from_string(subscriptions_data)
    yield from (subscription.xmlUrl for subscription in outline[0])


async def parse_feed(feed_data):
    f = await curio.run_in_thread(feedparser.parse, feed_data)
    for entry in f.entries:
        yield entry.id, {
            'author': entry.author,
            'title': entry.title,
            'link': entry.link,
            'downloaded': False,
            'dirty': False
        }
    logger.debug('parsed a feed')


async def grab_feed(semaphore, session, feed_url):
    async with semaphore:
        feed_resp = await session.get(feed_url)
    if feed_resp.status_code != 200:
        raise IOError(f'Could not get feed {feed_url}')
    logger.debug(f'grabbed {feed_url}')
    return feed_resp.text


async def download_video(semaphore, ytdl, video_url, video_id):
    try:
        async with semaphore:
            logger.debug(f'downloading {video_url}')
            await curio.workers.run_in_thread(ytdl.download, (video_url,))
            logger.debug(f'done downloading {video_url}')
    except CancellationRequestedError:
        pass
    return video_id


async def main_task(arguments):
    if arguments['--verbose']:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

    progress_model = DownloadProgressModel()
    YTDL_OPTS['progress_hooks'].append(progress_model.progress_hook)

    config = await read_json(arguments['--config'])
    if not config:
        config = {
            'videos': {}
        }
    for video in config['videos'].values():
        video['dirty'] = True

    async with curio.aopen(arguments['--subscriptions'], 'r') as f:
        subscriptions = await f.read()

    requests_semaphore = curio.BoundedSemaphore(value=25)
    requests_session = asks.DSession(connections=5)
    video_download_semaphore = curio.BoundedSemaphore(value=8)

    grabbers = curio.TaskGroup(name='grabbers')
    downloaders = curio.TaskGroup(name='downloaders')

    if not arguments['--verbose']:
        gui_task = await curio.spawn(gui, progress_model)

    for feed_url in parse_subscriptions(subscriptions):
        await grabbers.spawn(grab_feed(requests_semaphore, requests_session, feed_url))

    try:
        with youtube_dl.YoutubeDL(YTDL_OPTS) as ytdl:
            async for feed_data in grabbers:
                async for video_id, meta in parse_feed(feed_data.result):
                    if video_id not in config['videos']:
                        config['videos'][video_id] = meta
                    else:
                        config['videos'][video_id]['dirty'] = False

                    if config['videos'][video_id]['downloaded'] is False:
                        download_task = await downloaders.spawn(download_video, video_download_semaphore, ytdl, meta['link'], video_id)
                        progress_model.add_video(video_id, meta['title'], download_task)

        async for completed_download in downloaders:
            config['videos'][completed_download.result]['downloaded'] = True
    finally:
        config['videos'] = {k: v for k, v in config['videos'].items() if v['dirty'] is False}
        write_json(config, arguments['--config'])
