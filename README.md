# Surround --- The First Sublime Six Plugin

Things are bound to break along the way, but in the spirit of 'release early and release often'...

# How to Use

Six needs to find this plugin to register it. To make it happen:

1. Copy the `.py` files in this repo to `Packages\User\six`
2. Create a `sixrc.py` file in `Packages\User`

Include something like this in `sixrc.py` (inspired by my own):

```python
import sublime

# This line imports our custom Sublime Text command and registers our Six plugin.
# BTW, this will fail if Six isn't available. We need to cover that case one day...
from User.six.surround import *


def plugin_loaded():
    # Everything below this line is extra stuff that you can keep in this file too.
    # Just an example; follow your heart!
    settings = sublime.load_settings('Preferences.sublime-settings')

    # Define mappings if Six is enabled.
    if 'Six' not in settings.get('ignored_packages'):
        from Six._init_ import editor
        from Six.lib.constants import Mode

        editor.mappings.add(Mode.Normal, 'Y', 'y$')
        editor.mappings.add(Mode.Normal, '<Space>', ':')
        editor.mappings.add(Mode.Normal, ',pp', 'a()<Esc>ha')
```