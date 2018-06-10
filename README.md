# Surround – The First Sublime Six Plugin

Things are bound to break along the way,
but here we are in the spirit of ‘release early, release often’.

## How to Use

Six needs to find this plugin to register it.
To make it happen:

1. Copy the `.py` files in this repo to `Packages\User\six`
2. Create a `sixrc.py` file in `Packages\User` (any file name is fine)

Now include something like the following in `sixrc.py`
(inspired by my own):

```python
# Six configuration file. The unusual layout is needed to avoid errors if Six
# is being ignored or otherwise unavailable.
import logging
import os

import sublime

from User.six.surround import (
    _six_surround_change,
    surround,
    )


# Hook ourselves up to the Six logger.
_logger = logging.getLogger('Six.user.%s' % __name__.rsplit('.')[1])
_logger.info("loading Six configuration")


def plugin_loaded():
    settings = sublime.load_settings('Preferences.sublime-settings')

    if 'Six' in settings.get('ignored_packages'):
        return

    from Six._init_ import editor
    from Six.lib.constants import Mode

    # Init the Surround plugin. We must do this here because now we know that
    # Six is definitely available.
    try:
        surround()
    except ValueError as e:
        if str(e) == "cannot register keys (zs) twice for normal mode":
            # We have reloaded sixrc.py; ignore command registration error.
            pass
        else:
            raise
    except Exception as e:
        _logger.error("error while (re)loading %s" % __name__)
        _logger.error(e)

    # Mappings -- optional. Follow your ♡!
    editor.mappings.add(Mode.Normal, 'Y', 'y$')
    editor.mappings.add(Mode.Normal, '<Space>', ':')
    editor.mappings.add(Mode.Normal, ',pp', 'a()<Esc>ha')

```