Vectors
=======

PyStages provides the :class:`pystages.Vector` for basic vector manipulation.
Querying or setting the position of stages is done with instances of
:class:`pystages.Vector`.

.. code-block:: python

    pos = mystage.position
    print(f'Position: {pos}')
    mystage.position = Vector(100e-6, 0e-6, 0e-6)

The dimension of vectors is arbitrary and depends on the number of axis of the
controlled stage. In addition to indexing operator `[]`, the fourth first
elements of vectors can be accessed using the `x`, `y`, `z` and `w` attributes.

.. code-block:: python

    pos = mystage.position
    print(f'Position: {pos[0], pos[1], pos[2]}')
    print(f'Position: {pos.x, pos.y, pos.z}')

Position attribute details
--------------------------

The `position` property of stage instances return a detached
:class:`pystages.Vector`. Modifying the returned vector does not move the stage,
so the following code does not work as intended:

.. code-block:: python

    # Does NOT work
    mystage.position.x = 100

This should be written as:

.. code-block:: python

    # Move the X axis
    pos = mystage.position
    pos.x = 100
    mystage.position = pos

This is more verbose, but may prevent awkward situations where a user thinks he
has a copy of the position and then starts editing it.
