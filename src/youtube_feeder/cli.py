"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?
You might be tempted to import things from __main__ later, but that will cause
problems--the code will get executed twice:
 - When you run `python -m youtube_feeder` python will execute
   ``__main__.py`` as a script. That means there won't be any
   ``youtube_feeder.__main__`` in ``sys.modules``.
 - When you import __main__ it will get executed again (as a module) because
   there's no ``youtube_feeder.__main__`` in ``sys.modules``.

Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import errno
import json
import os
import sys
from time import sleep

import click
import feedparser
import opml
import pafy

APP_NAME = 'youtube_feeder'
CONFIG_LOCATION = click.get_app_dir(APP_NAME)
CONFIG_FILE = 'config.json'
SUBSCRIPTIONS_FILE = 'subscriptions.opml'


def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def read_JSON(path):
    """
    Attempt to read a JSON file. Returns False if the file doesn't exist.

    :param path: the path of the file to read
    """
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except IOError:
        return False


def write_JSON(to_write, path):
    """
    Write a serializable object to a JSON file.

    :param to_write: the object to write out
    :param path: the path of the file to output
    """
    ensure_dir(os.path.split(path)[0])
    with open(path, 'w') as f:
        json.dump(to_write, f, indent=2, sort_keys=True)


def merge_preserving_old_values_and_new_keys(old, new):
    out = {}
    for k, v in new.items():
        if k in old:
            out[k] = old[k]
        else:
            out[k] = v
    return out


def update_videos(subs):
    feeds = [subscription.xmlUrl for subscription in subs[0]]
    new_videos = {}
    for feed in feeds:
        f = feedparser.parse(feed)
        for entry in f.entries:
            new_videos[entry.id] = {
                'author': entry.author,
                'title': entry.title,
                'link': entry.link,
                'downloaded': False
            }
    return new_videos


def find_matching_dir(output_directory, title):
    dirs = []
    for (_, dirnames, _) in os.walk(output_directory):
        dirs.extend(dirnames)
        break
    for d in dirs:
        if title.startswith(d):
            return d


@click.command()
@click.option('--config', '-c', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--subscriptions', '-s', type=click.Path(dir_okay=False, resolve_path=True))
@click.option('--output-directory', '-o', type=click.Path(file_okay=False, resolve_path=True))
@click.option('--advanced-sorting/--no-advanced-sorting', default=True)
@click.version_option()
@click.pass_context
def main(ctx, config, subscriptions, output_directory, advanced_sorting):
    ensure_dir(CONFIG_LOCATION)
    if not config:
        config = os.path.join(CONFIG_LOCATION, CONFIG_FILE)
    configuration = read_JSON(config)
    if not configuration:
        configuration = {
            'settings': {},
            'videos': {}
        }

    if not subscriptions:
        subscriptions = os.path.expanduser(configuration['settings'].get(
            'subscriptions_file',
            os.path.join(CONFIG_LOCATION, SUBSCRIPTIONS_FILE)
        ))
    if not output_directory:
        output_directory = os.path.expanduser(
            configuration['settings'].get('output_directory', os.getcwd())
        )
    advanced_sorting = configuration['settings'].get('advanced_sorting', advanced_sorting)

    try:
        subs = opml.parse(subscriptions)
    except OSError:
        ctx.exit('Subscriptions file `{}` is missing'.format(subscriptions))
    new_videos = update_videos(subs)

    configuration['videos'] = merge_preserving_old_values_and_new_keys(
        configuration['videos'],
        new_videos
    )

    try:
        for v in configuration['videos'].values():
            if not v['downloaded']:
                sys.stdout.write('\033[K')
                print('{} by {}'.format(v['title'], v['author']))

                vid = pafy.new(v['link'])
                stream = vid.getbest()
                outdir = os.path.join(output_directory, v['author'])
                ensure_dir(outdir)
                if advanced_sorting:
                    outdir = os.path.join(
                        outdir,
                        find_matching_dir(outdir, v['title']) or ''
                    )
                path = os.path.join(outdir, stream.generate_filename(meta=False))

                try:
                    stream.download(filepath=path, quiet=False)
                    v['downloaded'] = True
                except KeyboardInterrupt:
                    sys.stdout.write('\033[K')
                    print('\nSkipping...press `^C` again within 1 second to exit')
                    sleep(1)
                    try:
                        os.unlink('{}.temp'.format(path))
                    except OSError as e:
                        if e.errno != errno.ENOENT:
                            raise
                    v['downloaded'] = True
                    continue
    finally:
        write_JSON(configuration, config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
