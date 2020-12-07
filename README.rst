youtube_feeder
==============
Feed you YouTube addiction, locally.


Installation
------------
Clone this repository and install with :code:`pip`::

    git clone https://github.com/scolby33/youtube_feeder.git
    cd youtube_feeder
    pip install .

Usage
-----
:code:`youtube_feeder` takes two inputs: a general configuration file and an
OPML file with the list of channels to download from.

Prepare the configuration file with contents along these lines and store it as
:code:`config.json` in the
`"app dir" <https://click.palletsprojects.com/en/7.x/api/#click.get_app_dir>`_
appropriate for your system.::

    {
      "settings": {
        "subscriptions_file": "/full/path/to/subscriptions.opml",
        "output_directory": "/full/path/to/video/output",
        "advanced_sorting": true
      }
    }

By default :code:`youtube_feeder` sorts videos into folders under the
:code:`output_directory` named after the channel they were downloaded from.
If :code:`advanced_sorting` is set to :code:`true`, the program will look under
this per-channel folder for a pre-existing folder whose name matches the
beginning of the video's name. For example, "My Series: Episode 1" would be
sorted into a folder named "My Series", if it exists.

Next, obtain your :code:`subscriptions.opml` file by visiting the
`YouTube Subscription Manager <https://www.youtube.com/subscription_manager>`_
and choosing the "Export subscriptions" button. Save this file to the location
defined in your :code:`config.json`.

Finally, call :code:`youtube_feeder` and, if everything has gone right, your
videos will begin to download.

If the default configuration location is inconvenient, you can use the
:code:`--config` option to point directly to the configuration file.
Additionally, the :code:`--subscriptions` and :code:`--output-directory`
options can be used to override those paths. Finally, the
:code:`--advanced-sorting/--no-advanced-sorting` options can be used to override
the advanced sorting setting from the configuration file.

Contributing
------------
Contributions are welcome! There are many ways to contribute to an open-source
project, but the two most common are reporting bugs and contributing code.

If you have a bug or issue to report, please visit the
`issues page on Github <https://github.com/scolby33/youtube_feeder/issues>`_
and open an issue there.

If you would like to contribute code, please open a pull request!

License
-------
MIT. See the :code:`LICENSE.rst` file for more information.
