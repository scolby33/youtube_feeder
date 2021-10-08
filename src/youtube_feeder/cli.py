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
from collections import Counter
import errno
import json
import os
from pathlib import Path
from pprint import pformat
import sys
from time import sleep
from typing import Any, AnyStr, Dict, Mapping, Optional, TypeVar, Union

import click
import click_pathlib
import feedparser
import opml
from tqdm import tqdm
import youtube_dl

APP_NAME = "youtube_feeder"
CONFIG_LOCATION = Path(click.get_app_dir(APP_NAME))
CONFIG_FILE = "config.json"
SUBSCRIPTIONS_FILE = "subscriptions.opml"
YTDL_CONFIG = {
    "format": "(bestvideo[vcodec^=av01][height>=1080][fps>30]/bestvideo[vcodec=vp9.2][height>=1080][fps>30]/bestvideo[vcodec=vp9][height>=1080][fps>30]/bestvideo[vcodec^=av01][height>=1080]/bestvideo[vcodec=vp9.2][height>=1080]/bestvideo[vcodec=vp9][height>=1080]/bestvideo[height>=1080]/bestvideo[vcodec^=av01][height>=720][fps>30]/bestvideo[vcodec=vp9.2][height>=720][fps>30]/bestvideo[vcodec=vp9][height>=720][fps>30]/bestvideo[vcodec^=av01][height>=720]/bestvideo[vcodec=vp9.2][height>=720]/bestvideo[vcodec=vp9][height>=720]/bestvideo[height>=720]/bestvideo)+(bestaudio[acodec=opus]/bestaudio)/best",
    "outtmpl": "%(title)s-%(id)s.%(ext)s",
    "writesubtitles": True,
    "allsubtitles": True,
    "postprocessors": [
        {"key": "FFmpegMetadata"},
        {"key": "FFmpegEmbedSubtitle"},
    ],
    "merge_output_format": "mkv",
    "call_home": False,
}

IGNORABLE_ERROR_PREFIXES = {
    "This live event will begin in",
    "Premieres in",
}

AnyPath = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]
OpenFile = Union[AnyPath, int]


def read_JSON(path: OpenFile) -> Optional[Any]:
    """
    Attempt to read a JSON file. Returns False if the file doesn't exist.

    :param path: the path of the file to read
    """
    try:
        with open(path, "r") as f:
            return json.load(f)
    except IOError:
        return None


def write_JSON(to_write: Any, path: os.PathLike[str]) -> None:
    """
    Write a serializable object to a JSON file.

    :param to_write: the object to write out
    :param path: the path of the file to output
    """
    path = Path(path)
    path.parent.mkdir(exist_ok=True, parents=True)
    with open(path, "w") as f:
        json.dump(to_write, f, indent=2, sort_keys=True)


OldKeys = TypeVar("OldKeys", bound=Any)
OldValues = TypeVar("OldValues", bound=Any)
NewKeys = TypeVar("NewKeys", bound=Any)
NewValues = TypeVar("NewValues", bound=Any)


def merge_preserving_old_values_and_new_keys(
    old: Mapping[OldKeys, OldValues], new: Mapping[NewKeys, NewValues]
) -> Dict[NewKeys, OldValues]:
    """Create a new dictionary with the same keys as new, but the same values as old,
    falling back to the values of new if the key is not present in old.

    For example:
        old = {"a": 1, "b": 1}
        new = {"b": 2, "c: 2}
        returns {"b": 1, "c": 2}
    """
    return {k: old.get(k, v) for k, v in new.items()}


def find_matching_dir(output_directory: os.PathLike[str], title: str) -> Optional[Path]:
    output_directory = Path(output_directory)
    if not output_directory.is_dir():
        # the output_directory doesn't exist, so it obviously has no subdirs
        return None
    for child in output_directory.iterdir():
        if child.is_dir() and title.startswith(str(child.name)):
            return child
    return None


@click.command()
@click.option(
    "--config", "-c", type=click_pathlib.Path(dir_okay=False, resolve_path=True)
)
@click.option(
    "--subscriptions", "-s", type=click_pathlib.Path(dir_okay=False, resolve_path=True)
)
@click.option(
    "--output-directory",
    "-o",
    type=click_pathlib.Path(file_okay=False, resolve_path=True),
)
@click.option("--advanced-sorting/--no-advanced-sorting", default=True)
@click.version_option()
@click.pass_context
def main(ctx, config, subscriptions, output_directory, advanced_sorting):
    if not config:
        CONFIG_LOCATION.mkdir(parents=True, exist_ok=True)
        config = CONFIG_LOCATION / CONFIG_FILE
    configuration = read_JSON(config)
    if not configuration:
        configuration = {"settings": {}, "videos": {}}

    if not subscriptions:
        subscriptions = Path(
            configuration["settings"].get(
                "subscriptions_file", CONFIG_LOCATION / SUBSCRIPTIONS_FILE
            )
        ).expanduser()

    if not output_directory:
        output_directory = Path(
            configuration["settings"].get("output_directory", Path.cwd())
        ).expanduser()

    advanced_sorting = configuration["settings"].get(
        "advanced_sorting", advanced_sorting
    )

    try:
        subs = opml.parse(str(subscriptions))
    except OSError:
        ctx.exit("Subscriptions file `{}` is missing".format(subscriptions))

    feeds = [subscription.xmlUrl for subscription in subs[0]]
    new_videos = {}
    click.echo("Downloading Feeds")

    statuses = Counter()

    try:
        for feed in tqdm(feeds):
            f = feedparser.parse(feed)
            sleep(0.25)  # be nice to youtube servers
            statuses.update((f.status,))
            if not (200 <= f.status < 300):
                click.echo(f"Error grabbing feed {feed}", err=True)
                continue
            for entry in f.entries:
                new_videos[entry.id] = {
                    "author": entry.author,
                    "title": entry.title,
                    "link": entry.link,
                    "downloaded": False,
                }
    finally:
        click.echo(f"Feed download status counts: {pformat(dict(statuses))}")

    configuration["videos"] = merge_preserving_old_values_and_new_keys(
        configuration.get("videos", {}), new_videos
    )
    write_JSON(configuration, config)

    ytdl = youtube_dl.YoutubeDL(YTDL_CONFIG)

    try:
        for vid in (
            vid for vid in configuration["videos"].values() if not vid["downloaded"]
        ):
            sys.stdout.write("\033[K")
            click.echo(f"*** {vid['title']} by {vid['author']}")

            outdir = output_directory / vid["author"]
            if advanced_sorting:
                outdir = find_matching_dir(outdir, vid["title"]) or outdir
            outdir.mkdir(parents=True, exist_ok=True)

            os.chdir(outdir)

            try:
                ytdl.download((vid["link"],))
                vid["downloaded"] = True
            except youtube_dl.utils.DownloadError as exc:
                for error_prefix in IGNORABLE_ERROR_PREFIXES:
                    try:
                        if exc.exc_info[1].args[0].startswith(error_prefix):
                            break
                    except:
                        # failed to parse the exception, so it's not one we know about
                        raise exc
                else:  # nobreak
                    raise
            except KeyboardInterrupt:
                sys.stdout.write("\033[K")
                click.echo("\nSkipping...press `^C` again within 1 second to exit")
                sleep(1)
                vid["downloaded"] = True
                continue
    finally:
        write_JSON(configuration, config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
