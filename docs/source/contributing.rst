.. only:: prerelease

    .. warning:: This is the documentation for a development version of youtube_feeder.

        .. only:: readthedocs

            `Documentation for the Most Recent Stable Version <http://youtube-feeder.readthedocs.io/en/stable>`_

.. _contributing:

Contributing
============

There are many ways to contribute to an open-source project, but the two most common are reporting bugs and contributing code.

If you have a bug or issue to report, please visit the `issues page on Github <https://github.com/scolby33/youtube_feeder/issues>`_ and open an issue there.

If you want to make a code contribution, check out the contributing page in the docs for more information.

.. note:: Remember to add yourself to :code:`AUTHORS.rst` if you make a code contribution!

Setup
-----

Here's how to get set up to contribute to :code:`youtube_feeder`.

#. Fork the :code:`youtube_feeder` repository on `GitHub <https://github.com/scolby33/youtube_feeder>`_
   (the fork button on the top right!)

#. If your change is small, you may be able to make it directly on GitHub via their online editing process.

   If your change is larger or you want to be able to run tests on your contribution, clone your forked repository locally::

    $ cd /your/dev/folder
    $ git clone https://github.com/your_username/youtube_feeder

   This will download the contents of your forked repository to :code:`/your/dev/folder/youtube_feeder`

#. If you're comfortable with a test-driven style of development, the only thing you need to install is `tox <http://tox.readthedocs.io/en/latest/>`_,
   either via the sometimes-temperamental but still useful `pipsi <https://github.com/mitsuhiko/pipsi>`_ (my choice), in a virtual environment,
   or just system-wide via pip::

    $ pipsi install tox
    # or
    $ pyvenv my-virtual-env
    $ source my-virtual-env/bin/activate
    $ pip install tox
    # or
    $ pip install tox

   With :code:`tox` installed, all tests, including checking the :code:`MANIFEST.in` file and code coverage can be performed just by executing::

    $ tox

   :code:`tox` handles the installation of all dependencies in virtual environments (under the :code:`.tox` folder) and the running of the tests.

   To develop like this, simply write your tests and your code and run :code:`tox` once in a while to check how you're doing.

   It is also possible to develop as usual by installing :code:`youtube_feeder` in editable mode with pip (preferably in a virtual environment)::

    $ cd /your/dev/folder/youtube_feeder
    $ cd pip install -e .

   Tests should still be run via :code:`tox`, but installing the package in this way gives you the flexibility to test things out in the REPL more easily.


Branches
--------

Development of :code:`youtube_feeder` follows the `"git flow" philosophy <http://nvie.com/posts/a-successful-git-branching-model/>`_ of branching.
Development takes place on the :code:`develop` branch with individual features being developed on feature branches off of develop.
Further reading on this style can be found in `this blog post <http://jeffkreeftmeijer.com/2010/why-arent-you-using-git-flow/>`_ by Jeff Kreeftmeijer.
A git plugin to aid in managing branches in this way, called :code:`git-flow`, can be found `here <https://github.com/nvie/gitflow>`_.

This might seem a bit complicated, but in general you won't have to worry about it as a contributor.
The long and short of this system for you is:

- make a new branch prefixed with "feature/" off of develop before starting work on your contribution
  (:code:`git checkout -b feature/descriptive-feature-name develop`)
- when pushing changes to your repository, push the right branch! (:code:`git push origin feature/descriptive-feature-name`)

The maintainers will take care of any other issues relating to this.

Pull Requests
-------------

Once you've got your feature or bugfix finished (or if its in a partially complete state but you want to publish it
for comment), push it to your fork of the repository and open a pull request against the develop branch on GitHub.

Make a descriptive comment about your pull request, perhaps referencing the issue it is meant to fix (something along the lines of "fixes issue #10" will cause GitHub to automatically link to that issue).
The maintainers will review your pull request and perhaps make comments about it, request changes, or may pull it in to the develop branch!
If you need to make changes to your pull request, simply push more commits to the feature branch in your fork to GitHub and they will automatically be added to the pull.
You do not need to close and reissue your pull request to make changes!

If you spend a while working on your changes, further commits may be made to the main :code:`youtube_feeder` repository (called "upstream") before you can make your pull request.
In keep your fork up to date with upstream by pulling the changes--if your fork has diverged too much, it becomes difficult to properly merge pull requests without conflicts.

To pull in upstream changes::

    $ git remote add upstream https://github.com/scolby33/youtube_feeder
    $ git fetch upstream develop

Check the log to make sure the upstream changes don't affect your work too much::

    $ git log upstream/develop

Then merge in the new changes::

    $ git merge upstream/develop

More information about this whole fork-pull-merge process can be found `here on Github's website <https://help.github.com/articles/fork-a-repo/>`_.

Code Style
----------

To make sure your contribution is useful to the overall :code:`youtube_feeder` project, you should follow a few conventions.

Run the Tests
^^^^^^^^^^^^^

Make sure your modifications still pass all tests before submitting a pull requests::

    $ tox

Changes that break the package are mostly useless.

Add New Tests
^^^^^^^^^^^^^

If you add functionality, you must add tests for it! Untested code is antithetical to reliability.
Pull requests that reduce code coverage will likely be rejected.
You can check your coverage in the output from :code:`tox`. Lines and files that lack test coverage will be noted there too!

Check out the tests (files that start with :code:`test_` under :code:`src/tests`) to see how previous tests have been written and match your new tests to this style.
Tests are performed with :code:`pytest`.

Try and keep your tests simple--tests shouldn't need tests for themselves! Some verbosity in tests isn't the end of the world if it helps to maintain clarity.

Keep Code Changes and Whitespace Cleanup Separate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is pretty self-explanatory. Code changes and whitespace cleanup should not be mixed--keep them in separate pull requests.

Keep Pull Requests Small
^^^^^^^^^^^^^^^^^^^^^^^^

Generally, pull requests should be targeted towards one issue. If you find yourself modifying large swathes of code spanning multiple fixes, thing about splitting your pull request into two (or more!) smaller ones.
Large pull requests will likely be rejected.

Follow PEP-8 (ish) and the Zen of Python
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you haven't before, check out the Zen of Python (:code:`python -c 'import this'`) and attempt to keep your code in line with its philosophy.
Simple is better than complex!

Keep best practices for formatting Python code in mind when writing your contribution. `PEP-8 <https://www.python.org/dev/peps/pep-0008/>`_ is generally followed in this project, but not pedantically. Line lengths, for example, are often allowed to creep up if it seems reasonable.
If you haven't seen Raymond Hettinger's `Beyond PEP 8 <https://www.youtube.com/watch?v=wf-BqAjZb8M>`_ presentation, I urge you to go watch it.
Unthinking adherence to the "rules" of PEP-8 is not demanded nor is it the best way to write good, Pythonic code.

Making a Release
----------------

The steps for making a release of :code:`youtube_feeder` are:

