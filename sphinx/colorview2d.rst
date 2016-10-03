colorview2d package
===================

.. automodule:: colorview2d.__init__

This documentation is not complete. It includes only the central
classes of colorview2d, which are

- the :class:`colorview2d.CvFig` class which hosts the *pipeline*, the *datafile* and the *configuration* objects.
- the :class:`colorview2d.Datafile` class which hosts the 2d numpy array and the axes bounds.


Classes
-------

CvFig: The colorview2d figure.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: colorview2d.CvFig
   :members:

Datafile: A container for the array and the axes bounds.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: colorview2d.Datafile
    :members:
    :undoc-members:
    :show-inheritance:

       
Configuration
-------------
Cvfig class has a config attribute. The parameters stored in its dictionary are
read from default.cv2d config file.

.. include:: ../colorview2d/default.cv2d
             :literal:
                    
---------------------------

..
   colorview2d.fileloaders module
   ------------------------------

   .. automodule:: colorview2d.fileloaders
       :members:
       :undoc-members:
       :show-inheritance:

   colorview2d.imod module
   -----------------------

   .. automodule:: colorview2d.imod
       :members:
       :undoc-members:
       :show-inheritance:

   colorview2d.utils module
   ------------------------

   .. automodule:: colorview2d.utils
       :members:
       :undoc-members:
       :show-inheritance:


   Module contents
   ---------------

   .. automodule:: colorview2d
       :members:
       :undoc-members:
       :show-inheritance:



   Subpackages
   -----------

   .. toctree::

      colorview2d.mods










