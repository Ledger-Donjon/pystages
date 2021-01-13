Autofocus
=========

The class :class:`pystages.Autofocus` eases focusing the Z-axis of a stage onto
a tilted XY plane. Given the correct Z position of three points on the XY plane,
the helper class can calculate the correct Z position for any arbitrary point on
the plane.

.. code-block:: python

    af = Autofocus()

    # Register three correct points
    af.register(0, 0, 12)
    af.register(1, 0, 12.1)
    af.register(0, 1, 12.2)

    # Get the correct Z position for another point
    z = af.focus(1, 1)
