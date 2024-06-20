# PyStages

[![Documentation Status](https://readthedocs.org/projects/pystages/badge/?version=latest)](https://pystages.readthedocs.io/en/latest/?badge=latest)

PyStages is a Python 3 library for controlling motorized stages which have a
motion controller. It has been designed for microscopy test benches automation.

The following motion controllers are currently supported (only the main features
are implemented):

- Micos Corvus Eco controller
- New Scale Technologies M3-FS focus modules (serial only)
- Newport SMC100 motion controllers
- Tic Stepper Motor controller (USB only)
- CNC Router with GRBL/GCode instructions (CNC 3018-PRO)

The library also provides helper classes for basic vector manipulation and
autofocus computation.

## Documentation

Documentation is available on [Read the Docs](https://pystages.readthedocs.io).

## PyStages GUI

A user interface has been implemented to control the stages.

You can run it with the following command:

```bash
python -m pystages.gui
```

## Requirements

This library requires the following packages:

- [pyserial](https://pypi.org/project/pyserial/)
- [numpy](https://pypi.org/project/numpy/)
- [pyusb](https://pypi.org/project/pyusb/)
- [PyQt6](https://pypi.org/project/PyQt6/)
