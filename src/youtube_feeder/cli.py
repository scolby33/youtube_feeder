"""youtube_feeder.

Usage:
    youtube_feeder (-c CONFIG | --config=CONFIG) (-s SUBSCRIPTIONS | --subscriptions=SUBSCRIPTIONS) [-v | --verbose]
    youtube_feeder (-h | --help)
    youtube_feeder --version

Options:
    -h --help                                       Show this screen.
    --version                                       Show the version.
    -c CONFIG --config=CONFIG                       The config file.
    -s SUBSCRIPTIONS --subscriptions=SUBSCRIPTIONS  The subscriptions file.
    -v --verbose                                    Verbose logging, disable GUI.
"""
import logging
import selectors
import socket

import curio
import docopt

from .downloader import main_task

logger = logging.getLogger(__name__)

dummy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def main():
    arguments = docopt.docopt(__doc__, version='youtube_feeder 0.1.0')

    selector = selectors.DefaultSelector()
    selector.register(dummy_socket, selectors.EVENT_READ)
    curio.run(main_task, arguments, selector=selector)

if __name__ == '__main__':
    main()
