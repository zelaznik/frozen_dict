C:
CD C:\users\szelazni\desktop\github\frozen_dict

python2 setup.py build_ext
IF %ERRORLEVEL% GEQ 1 GOTO HANDLER

python2 setup.py install
IF %ERRORLEVEL% GEQ 1 GOTO HANDLER

python2 frozen_dict__unittest.py

:HANDLER
pause
