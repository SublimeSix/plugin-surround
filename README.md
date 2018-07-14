[![Build Status](https://travis-ci.org/SublimeSix/plugin-surround.svg?branch=master)](https://travis-ci.org/SublimeSix/plugin-surround)

## Surround – The First Sublime Six Plugin

This plugin is functional but under constant development.

The surround plugin adds a few commands
to opearte on delimiters.
For example, given the following line
(where `^` denotes the caret)

    one "two" three
         ^ 

the command `cs"'` would produce

    one 'two' three

Similarly, `ds"` would produce

    one two three

### Installation

Six needs to find this plugin to register it.
To make it happen:

1. Copy the `.py` files in this repo to `Packages/User/six`
2. Create a `sixrc.py` file in `Packages/User` (the file name doesn't really matter)

Now include in it something like the [sample sixrc.py file](https://github.com/SublimeSix/sample-sixrc/blob/master/sixrc.py).

### Developing Surround

First, clone this repository:

    $ git clone https://github.com/SublimeSix/plugin-surround.git

Install `pipenv` if you don't have it yet:

    $ pip install --upgrade pip
    $ pip install pipenv

Create a virtual environment to develop Surround in:

    $ cd path/to/this/repo
    $ pipenv install

Activate the virtual environment:

    $ pipenv shell

Now your new virtual environment should be ready.
You can check which python interpreter is being used
for confirmation:

    $ which python # Unix
    $ where.exe python # Windows
    $ gcm python | slo source # PowerShell

Surround strives to conform to Python's PEP8 code style guidelines
and delegates code formatting to a tool.

Here's the list of the main code analyzers used:

- `yapf`
- `flake8`
- `pylint`


#### Running the Test Suite

To run the tests,
you need to install the following requirements:

- UnitTesting package (via PackageControl)

Then, you need to copy the _unittesting.json_ file in this repostitory
to _Packages/User_.
This is required
so that UnitTesting
can find the tests under _Packages/User/six/tests_.

When you run the tests in UnitTesting,
give it the *User* package name.


#### Credits

The surround plugin
is a port of [vim surround](https://github.com/tpope/vim-surround).