"""Supervision management utilities.
"""

from __future__ import absolute_import

import io
import errno
import logging
import os
import re

_ENV_KEY_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_.]*$')
_LOGGER = logging.getLogger(__name__)


def data_read(filename):
    """Read a file.

    :returns ``unicode``:
        File content.
    """
    with open(filename) as f:
        data = f.readline()
    return data.decode(encoding='utf8').strip()


def data_write(filename, data):
    """Writes a file.

    :param``unicode`` data:
        File content.
    """
    with open(filename, 'w') as f:
        if data is not None:
            f.write(data.encode(encoding='utf8', errors='replace') + '\n')
        if os.name == 'posix':
            os.fchmod(f.fileno(), 0o644)


def environ_dir_write(env_dir, env, update=False):
    """Create environment directory suitable for envdir.

    :params ``str`` env_dir:
        Directory to use as the envdir. Must exist.
    :params ``dict`` env:
        Key/Value pairs to define in the environ directory. Values can have
        unicode data.
    :param ``bool`` update:
        If ``False``, set to directory to the content of the dictionary. If set
        to ``True``, then add/set the new Key/Value pairs from the dictionary
        but leave other values in the directory.
    """
    if not update:
        for key in os.listdir(env_dir):
            if key not in env:
                os.unlink(os.path.join(env_dir, key))

    for key, value in env.iteritems():
        if not _ENV_KEY_RE.match(key):
            _LOGGER.warning('Ignoring invalid environ variable %r', key)
            continue

        with open(os.path.join(env_dir, key), 'w+') as f:
            if value is not None:
                # The value must be properly escaped, all tailing newline
                # should be removed and the newlines replaced with \0
                data = (
                    unicode(value)
                    .encode(encoding='utf8', errors='replace')
                    .rstrip(b'\n')
                    .replace(b'\n', b'\x00')
                )
                f.write(data)
                if os.name == 'posix':
                    os.fchmod(f.fileno(), 0o644)


def environ_dir_read(env_dir):
    """Read an environment directory back into a dictionary.

    :params ``str`` env_dir:
        Directory to use as the envdir. Must exist.
    :returns ``dict``:
        Key/Value pairs defined in the environ directory. Values can have
        unicode data.
    """
    env = {}
    for key in os.listdir(env_dir):
        with open(os.path.join(env_dir, key)) as f:
            data = f.readline()
        value = (
            data
            .strip()
            .replace(b'\0', b'\n')
            .decode(encoding='utf8')
        )
        env[key] = value

    return env


def set_list_read(filename):
    """Read a list of values, one per line.

    :param ``str`` filename:
        Name of the file to read.
    :returns ``set``:
        Set of values read from ``filename``. Value can be unicode.
    """
    try:
        with open(filename) as f:
            entries = f.read().strip().split('\n')
    except IOError as err:
        if err.errno is errno.ENOENT:
            entries = set()
        else:
            raise

    return {
        entry.decode(encoding='utf8')
        for entry in entries
        if entry
    }


def set_list_write(filename, entries):
    """Write a list of values to a file. One per line.

    :param ``str`` filename:
        Name of the file to read.
    :param ``set`` entries:
        Set of values to write into ``filename``. Value can be unicode.
    """
    values = {
        unicode(entry).encode(encoding='utf8', errors='replace')
        for entry in entries
    }
    with open(filename, 'w') as f:
        f.writelines(values)
        if os.name == 'posix':
            os.fchmod(f.fileno(), 0o644)


def value_read(filename, default=0):
    """Read an integer value from a file.

    :param ``str`` filename:
        File to read from.
    :param ``int`` default:
        Value to return in case `filename` doesn't exist.
    :returns ``int``:
        Value read or default value.
    """
    try:
        with open(filename) as f:
            value = f.readline()
    except IOError as err:
        if err.errno is errno.ENOENT:
            value = default
        else:
            raise
    return int(value)


def value_write(filename, value):
    """Write an integer value to a file.

    :param ``str`` filename:
        File to write to.
    :param ``int`` value:
        Value to write in the file.
    """
    with open(filename, 'w') as f:
        f.write('%d\n' % value)
        if os.name == 'posix':
            os.fchmod(f.fileno(), 0o644)


def script_read(filename):
    """Read a shell script from a file.

    :param ``str`` filename:
        File to read from.
    :returns ``unicode``:
        Script read from the file.
    """
    with open(filename, 'r') as f:
        script = f.read()
    return script.decode(encoding='utf8')


def script_write(filename, script):
    """Write a script to a file.

    Proper execute permissions will be set.

    :param ``str`` filename:
        File to write to.
    :param ``script:
        String or iterable returning strings. Can be unicode.
    """
    if isinstance(script, basestring):
        # If the script is fully provided in a string, wrap it in a StringIO
        script = io.StringIO(unicode(script))

    with open(filename, 'w') as f:
        for chunk in script:
            # The value must be properly encoded
            data = (
                unicode(chunk)
                .encode(encoding='utf8', errors='replace')
            )
            f.write(data)
        if os.name == 'posix':
            os.fchmod(f.fileno(), 0o755)


__all__ = (
    'data_read',
    'data_write',
    'environ_dir_read',
    'environ_dir_write',
    'script_read',
    'script_write',
    'set_list_read',
    'set_list_write',
    'value_read',
    'value_write',
)