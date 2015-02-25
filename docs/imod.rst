The plugin interface
~~~~~~~~~~~~~~~~~~~~

The plugin interface consists of two modules, the

:IMod: class interface specification
:ModWidget: widget base class

Please have a look at specific plugin implementations
for examples.

.. automodule:: colorview2d.IMod
   :members:


.. module:: colorview2d.ModWidget

ModWidget
---------

Module provides the base class for plugin widgets.

It contains a checkbox widget and can be used
directly in a mod plugin.

.. class:: ModWidget

   Base class for the plugin widgets that can be provided
   to colorview2d.

   The widget is a descendant of `wx.BoxSizer <http://www.wxpython.org/docs/api/wx.BoxSizer-class.html>`_.
   Childs should call init and update upon overwrite.

   :ivar mod: The mod class this widget is assigned to
   :ivar panel: The panel this widget lives on
   :ivar title: The title of the mod.
   :ivar chk: A handle for the checkbox widget.

   .. method:: update()

      Update the mod widget to comply with the state of the mod.
      Should update all widgets contained in the ModWidget descendant.

   .. method:: on_chk(event)

      Handler for the *event* that is triggered by activating/deactivating
      the checkbox.

      It is not required to overwrite this function in a custom plugin implementation.


