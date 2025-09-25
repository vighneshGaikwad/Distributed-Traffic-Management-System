@ECHO OFF
TITLE Traffic System Launcher

ECHO Starting all three servers in separate windows...
ECHO.

:: Start the Signal Manipulator Server
ECHO Starting signal_manipulator_server.py...
START "Manipulator Server" cmd /k python signal_manipulator_server.py

:: Give it a moment to initialize before starting the next one
TIMEOUT /T 2 > NUL

:: Start the Pedestrian Controller Server
ECHO Starting pedestrian_controller_server.py...
START "Pedestrian Server" cmd /k python pedestrian_controller_server.py

:: Give it a moment to initialize
TIMEOUT /T 2 > NUL

:: Start the Main Signal Controller and UI Server
ECHO Starting signal_controller_server.py...
START "Main Controller (UI)" cmd /k python signal_controller_server.py

ECHO.
ECHO All servers have been launched. You can close this window.
PAUSE