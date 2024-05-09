@echo off
:start

:: Start the python script
start /B C:\Users\tjasr\AppData\Local\Programs\Python\Python312\python.exe LIBS_Back/controller.py

:: Start Node-RED
start /B node-red

:: Open the browser
start http://127.0.0.1:1880/ui

:: Wait for a Ctrl+C
:loop
pause
tasklist | find /i "python.exe" || taskkill /f /im python.exe
tasklist | find /i "node.exe" || taskkill /f /im node.exe
goto loop