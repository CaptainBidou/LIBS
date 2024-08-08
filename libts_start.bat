@REM start of mysql server xampp
cd C:/xampp
@REM create a thread for mysql server
start /b mysql_start.bat 

echo "mysql server started"

@REM start of apache server xampp
start /b apache_start.bat 
echo "apache server started"


@REM start of angular project
cd C:\LIBS-FRONT\liion-master
start ng serve
echo "angular project started"




@REM start of controller.py
cd C:\LIBS\Back
start c:\ProgramData\anaconda3\python.exe controller.py 
echo "controller.py started"

@REM open browser
start http://localhost:4200