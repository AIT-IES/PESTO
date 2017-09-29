@echo off
net user administrator /active:yes
echo Set password for Administrator:
net user administrator *
Netsh advfirewall firewall set rule group="Remote Service Management" new enable=yes
Netsh advfirewall firewall set rule group="File and Printer Sharing" new enable=yes
pause