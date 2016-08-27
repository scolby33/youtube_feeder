.. only:: prerelease

    .. warning:: This is the documentation for a development version of youtube_feeder.

        .. only:: readthedocs

            `Documentation for the Most Recent Stable Version <http://youtube-feeder.readthedocs.io/en/stable>`_

.. _installation:

Installation
============

There are many ways to install a Python package like :code:`youtube_feeder`. Here many of those will be explained and the advantages of each will be identified.

If you are not yet familiar with virtual environments, stop reading this documentation and take a few moments to learn. Try some searches for "virtualenv," "virtualenvwrapper," and "pyvenv."
I promise that they will change your (Python) life.

Where to Get the Code
---------------------

From PyPI
^^^^^^^^^

Stable releases of :code:`youtube_feeder` are located on PyPI, the `PYthon Package Index <https://pypi.python.org/pypi>`_.
Installation from here is easy and generally the preferred method::

    $ pip install youtube_feeder


From GitHub
^^^^^^^^^^^

:code:`pip` is also able to install from remote repositories. Installation from this project's GitHub repo can get you the most recent release::

    $ pip install git+https://github.com/scolby33/youtube_feeder@master#egg=youtube_feeder-latest

This works because only release-ready code is pushed to the master branch.

To get the latest and greatest version of :code:`youtube_feeder` from the develop branch, install like this instead::

    $ pip install git+https://github.com/scolby33/youtube_feeder@develop#egg=youtube_feeder-latestdev

In both of these cases, the :code:`#egg=youtube_feeder_complete-version` part of the URL is mostly arbitrary. The :code:`version` part is only useful for human readability and the :code:`youtube_feeder` part is the project name used internally by :code:`pip`.

From a Local Copy
^^^^^^^^^^^^^^^^^

Finally, :code:`pip` can install from the local filesystem::

    $ cd /directory/containing/youtube_feeder/setup.py
    $ pip install .

Installing like this lets you make changes to a copy of the project and use that custom version yourself!

Installing in Editable Mode
---------------------------

:code:`pip` has a :code:`--editable` (a.k.a. :code:`-e`) option that can be used to install from GitHub or a local copy in "editable" mode::

    $ pip install -e .

This, in short, installs the package as a symlink to the source files. That lets you edit the files in the :code:`src` folder and have those changes immediately available.
