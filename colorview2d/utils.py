"""Utility functions for different purposes."""
import os
import sys
import logging
import yaml

import six

def resource_path(relative_path):
    """Return the absolute path to a resource"""
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
        logging.info('Packed to an executable, application path: %s', application_path)
    else:
        application_path = os.path.dirname(__file__)
        logging.info('Resource path: %s', application_path)

    return os.path.join(application_path, relative_path)

class Config(yaml.YAMLObject):
    """A class to host the configuration of the :class:`colorview2d.View`
    class.
    """
    # the default_config_file is used to initialize a valid set of parameters
    _default_config_file_path = resource_path('default.cv2d')
    yaml_tag = u'!Config'
    def __init__(self, *args, **kwargs):
        """Read the default config file and update it with any given arguments.
        """
        with open(self._default_config_file_path) as cfgfile:
            doclist = yaml.load_all(cfgfile)
            # The config dict is the first yaml document
            self._dict = dict(six.advance_iterator(doclist))


        self.update(*args, **kwargs)

    def __repr__(self):
        return repr(self._dict)

    def __getitem__(self, key):
        return self._dict[key]

    def __setitem__(self, key, value):
        """We overwrite setitem to avoid populating the parameter set
        with any invalid parameters without noticing.
        """
        self.set(key, value)

    def set(self, key, value):
        if key not in self._dict.keys():
            raise KeyError('Not a valid configuration key %s.' % key)

        self._dict[key] = value
        self.on_change(key, value)


    def on_change(self, key, value):
        """Hook to react to a change in any parameter.
        Has to be overwritten by :class:`colorview2d.View` class.

        Note: This is intended to update the plot upon parameter changes.
        """
        pass


    def update_raw(self, *args, **kwargs):
        """Update the config dict without invoking the post update hook on_change().
        """
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self._dict[key] = other[key]


        for key in kwargs:
            self._dict[key] = kwargs[key]


    def update(self, *args, **kwargs):
        """Update the dict. Note that we call __setitem__ on each item
        so that on_change is triggered, as opposed to update_raw."""
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self.set(key, other[key])
        for key in kwargs:
            self.set(key, kwargs[key])

    @property
    def dict(self):
        return self._dict


def fontlist():
    """Obtain a list of the fonts that are found by matplotlib."""
    import matplotlib.font_manager as fm

    flist = fm.findSystemFonts()

    fontliststrings = [fm.FontProperties(fname=fname).get_name() for fname in flist]
    # remove duplicates
    fontliststrings = list(set(fontliststrings))
    return fontliststrings.sort()


def colormaplist():
    """Obtain a list of colormaps which are available in matplotlib."""
    from matplotlib.pyplot import cm
    maps = [m for m in cm.datad if not m.endswith("_r")]
    return maps.sort()









