@echo off

set clients=%0
set clients=%clients:test.bat=clients.txt%

runas /savecred /user:administrator "psexec /accepteula @%clients% python c:\client-test\test.py"

pause