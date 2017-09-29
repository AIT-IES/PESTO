"""
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.
 
 All rights reserved. See file PESTO _LICENSE for details.



PESTO.py

creates GUI using Gooey
2 parameters through GUI -> master.py and .json file
calls master.py with the selected settings

lauchWithoutConsole -> subprocess wont open new window, the output will be written to stdout

PESTO.py was genereted to an executable -> PESTO.exe (pyinstaller --onefile --windowed pesto.py)
"""



from gooey import Gooey, GooeyParser
import subprocess

def launchWithoutConsole(command):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(command, startupinfo=startupinfo, stdout=subprocess.PIPE, universal_newlines=True)
    for line in p.stdout:
        print(line, flush=True)




@Gooey()
def main():

    parser = GooeyParser(description='Load settings for PESTO')

    parser.add_argument('PESTO Master', help="Choose PESTO-master\master.py.", widget='FileChooser')

    parser.add_argument('Settings file', help="Choose the settings file.", widget='FileChooser')

    args = parser.parse_args()
    settingsfile = vars(args)['Settings file']
    master = vars(args)['PESTO Master']
    command = 'python -u ' + master + ' ' + settingsfile
    launchWithoutConsole(command)


if __name__ == '__main__':
  main()
