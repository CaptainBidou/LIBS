@REM start of mysql server xampp
cd C:/xampp
@REM create a thread for mysql server
start /b mysql_stop.bat 

echo "mysql server stopped"

@REM start of apache server xampp
start /b apache_stop.bat 
echo "apache server stopped"

