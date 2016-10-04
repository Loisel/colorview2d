
"""
IMod
----

Interface to the mod plugin class.
Specification of the minimum requirements of a plugin implementation.
"""

import logging
import abc


class IMod(object):
    """
    The interface class is an abstract base class.
    At present, none of the methods have to be overwritten, though.

    Args:
        title (string): Title string of the plugin. Usually equal to the
                  plugin/module name.
        default_args (tuple): A default set of arguments that works with the apply function.
    """
    __meta__ = abc.ABCMeta
    def __init__(self):
        """
        The init function should be called by the plugin implementation
        to correctly initialize the title and provide logging.
        """
        self.default_args = ()

        self.title = self.__class__.__name__
        logging.info('Mod %s is initialized.' % self.title)

        
    def apply(self, data, modargs):
        """
        This method provides a hook for do_apply which has to be
        overwritten by any mod implementation to provide some useful functionality.
        
        ValueErrors and TypeErrors appearing in do_apply are caught and the View object
        is informed of the failure and deactivates the mod.

        Args:
            data (colorview2d.Data): A data object.
            modargs (tuple): the arguments required to apply the mod.
        """

        if 'do_apply' not in dir(self):
            logging.warning('Mod %s has not implemented the do_apply method.', self.title)
        else:
            try:
                self.do_apply(data, modargs)
                if len(data.zdata.shape) != 2:
                    logging.warn(
                        'Mod %s failed. The mod changed the dimensionality of the data.zdata array.',
                        self.title)
                    return False
                return True
            except ValueError:
                logging.warn(
                    'Mod %s failed. Value Error. Probably you supplied unusable arguments. Args: %s',
                    self.title,
                    modargs)
                return False
            except TypeError:
                logging.warn(
                    'Mod %s failed. Type Error. Have you supplied the correct argument type? Args: %s',
                    self.title,
                    modargs)
                return False
            except MemoryError:
                logging.warn(
                    'Mod %s failed. Not enough memory. Try different parameters. Args: %s', self.title, modargs)
                return False
















