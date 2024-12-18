:: ELASTIC SEARCH GUI by SIDDHARTH SINGH (siddharth_singh) on 06/28/2020
@echo off
if not DEFINED IS_MINIMIZED set IS_MINIMIZED=1 && start "" /min "%~dpnx0" %* && exit
echo Please wait while the necessary packages get installed...

echo RUNNING ELASTIC SEARCH GUI...

cd=%cd%

cd %cd%\code

python ui.py

exit