@REM start of mysql server xampp
cd C:/xampp
@REM create a thread for mysql server
start /b mysql_start.bat 

echo "mysql server started"

@REM start of apache server xampp
start /b apache_start.bat 
echo "apache server started"


@REM start of angular project
cd C:\Users\tjasr\Documents\GitHub\LIBS\LIBS_Front\liion
start ng serve
echo "angular project started"

@REM open browser
start http://localhost:4200


@REM start of controller.py
cd C:/Users/tjasr/Desktop/LIBS-test/LIBS/Back
c:/Python311/python.exe controller.py 
echo "controller.py started"