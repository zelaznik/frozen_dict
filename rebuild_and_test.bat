C:
CD C:\users\szelazni\desktop\github\frozen_dict

python3 setup.py build_ext
IF %ERRORLEVEL% GEQ 1 GOTO HANDLER

python3 setup.py install
IF %ERRORLEVEL% GEQ 1 GOTO HANDLER

python3 frozen_dict__unittest.py

:HANDLER
pause
