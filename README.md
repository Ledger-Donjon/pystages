# PyStages

PyStages is a Python 3 library for controlling motorized stages which have a
motion controller. It has been designed for microscopy test benches automation.

The following motion controllers are currently supported (only the main features
are implemented):

- Micos Corvus Eco controller
- New Scale Technologies M3-FS focus modules (serial only)
- Newport SMC100 motion controllers
- Tic Stepper Motor controller (USB only)

The library also provides helper classes for basic vector manipulation and 
autofocus calculation

## Requirements

This library requires the following packages:
- pyserial
- numpy

