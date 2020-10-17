import yaml
import os.path
import logging

log = logging.getLogger(__name__)


class PathChainer:
    def __init__(self, parent, name=None, attr_access=False):
        self._name = name
        self._parent = parent
        self._attr_access = attr_access

    def __getattr__(self, name):
        return PathChainer(self, name, attr_access=True)

    def __getitem__(self, name):
        return PathChainer(self, name)

    def __call__(self, *args, **kwargs):
        return self.__evalitem__([], *args, **kwargs)

    def __evalitem__(self, path_components, *args, **kwargs):
        newpath = path_components
        if self._name is not None:
            newpath = [(self._name, self._attr_access)]+newpath
        if isinstance(self._parent, PathChainer):
            return self._parent.__evalitem__(newpath, *args, **kwargs)
        return self._parent(newpath, *args, **kwargs)


def follow_path(source, path):
    cursor = source
    for name, attr_access in path:
        cursor = cursor[name]
    return cursor


def try_sources(path_components, *args, **kwargs):
    values = []
    for src in reversed(_sources):
        try:
            if isinstance(src, dict):
                values.append(follow_path(src, path_components))
            if callable(src):
                values.append(src(path_components))
        except KeyError:
            pass
    if len(values) == 0:
        if 'default' in kwargs:
            return kwargs['default']
        if len(args) > 0:
            return args[0]
        raise KeyError()

    if len(values) > 1 and 'raw' in kwargs and kwargs['raw']:
        return values
    return values[0]


_sources = []
config = PathChainer(try_sources)


def config_add(source):
    if type(source) == list:
        for s in source:
            config_add(s)
    if type(source) == str:
        if not os.path.isfile(source):
            log.warning(f'Config file "{source}" does not exist')
            return
        with open(source, 'r') as f:
            _sources.append(yaml.safe_load(f.read()))
        return
    _sources.append(source)
