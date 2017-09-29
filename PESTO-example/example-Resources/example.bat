@echo off

@echo PESTO - Example>%1.txt
@echo %username%>>%1.txt
@echo %computername%>>%1.txt

echo File, %1.txt was written.