# PyStages GUI

A user interface has been implemented to control the stages.

You can run it with the following command:

```bash
python -m pystages.gui
```

This tool presents basic controls. After connection to the stage, it polls the position and prints out
at the bottom of the window.

## Stage selection and connection

Select the type of stage that you want to control and chose either a serial port to connect to, or select `Auto detect`
to make pystage to select the correct one according to the device description.

Then click to `Connect`. If the connection success, the control buttons are activated.

## Relative move

You can click on buttons to move for a positive of negative relative distance. 
The direction correspond to the axis number of the stage (`X` for first axe, `Y` for the second one,
`Z` for the third one). The moving distance is selected throug the `Step` dropdown menu.

## Absolute move

You can enter absolute coordinates in the 3 entry boxes and trigger the move by clicking the `Go To Position` button.

## Z offset

The `Z offset` checkbox and dropdown menu permit for each horizontal move (X or Y)
to make first a vertical-up displacement (Z+) followed by the
actual move, and then a final vertical-down displacement (Z-).

## Homing

The `Home` button permits to trigger the calibration process of the stage. 
Be careful that your setup is clear before using it.

