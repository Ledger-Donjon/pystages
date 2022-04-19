Troubleshooting
===============

M3-FS connection fails
----------------------

If the USB-to-Serial device is visible by the operating system but connecting
to the M3-FS module fails, verify your USB port provides enough current to power
the instrument.

Under Linux, the device may not work if the default baudrate setting is 250000
bps. In that case, using Windows, reconfigure the default baudrate to be 115200
bps.
