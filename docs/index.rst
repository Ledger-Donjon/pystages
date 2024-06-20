Welcome to pystages's documentation!
====================================

PyStages is a Python 3 library for controlling motorized stages which have a
motion controller. It has been designed for microscopy test benches automation.

The following motion controllers are currently supported (only the main
features are implemented):

- Newport SMC100 Single-Axis DC or Stepper Motion Controller
  (:class:`pystages.smc100.SMC100`)
- SMC Corvus Stepper Motor Controller (:class:`pystages.corvus.Corvus`)
- New Scale M3-FS Focus Module (:class:`pystages.m3fs.M3FS`)
- CNC Router, controlled with GRBL/GCode instructions (CNC 3018-PRO)
  (:class:`pystages.cncrouter.CNCRouter`)

The library also provides helper classes for basic vector manipulation
(:class:`pystages.Vector`) and autofocus calculation
(:class:`pystages.Autofocus`).

.. toctree::
  :maxdepth: 2
  :caption: Contents:

  Vectors <vectors.rst>
  Autofocus <autofocus.rst>
  Python API <api.rst>
  GUI <gui.md>
  Troubleshooting <troubleshooting.rst>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
