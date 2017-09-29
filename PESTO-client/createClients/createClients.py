"""
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.
 
 All rights reserved. See file PESTO _LICENSE for details.



 PESTO-client\createClients\createClients.py

 for 1 user:
   enables communication on ports
   creates working directory if needed
   executes PESTO-client\Instance\Instance.py as Administrator or as a specified user
   deletes working directory
   closes ports

 for more users:
   creates working directory with subdirectory for all users
   enables communication on ports
   creates windows users
   executes PESTO-client\Instance\Instance.py as the created users
   deletes windows users
   deletes workingdirectory
   closes ports
"""

import subprocess
import sys
import os
import shutil
import time



def createWorkingDirectory(workingdir):
    """
    creates working directory if it doesnt exist.
    """

    print('Creating: ' + workingdir, flush=True)
    if not os.path.isdir(workingdir):
        try:
            os.makedirs(workingdir)
        except Exception as e:
            print('Error creating the working directory\n', flush=True)
            print(e, flush=True)
            return 1
    return 0




def createWorkingDirectories(workingdir, number_of_users):
    """
    creates working directories for all users
    """

    for i in range(number_of_users):
        newpath = workingdir+'\\MyUser'+str(i)
        print('Creating: ' + newpath, flush=True)
        if not os.path.isdir(newpath):
            try:
                os.makedirs(newpath)
            except Exception as e:
                print('Error creating the directory\n', flush=True)
                print(e, flush=True)
                return 1
    return 0




def deleteWorkingDirectory(workingdir):
    """
    deletes working directory
    """

    if os.path.isdir(workingdir):
        print('Deleting: ' + workingdir, flush=True)
        try:
            shutil.rmtree(workingdir, ignore_errors=False)
        except Exception as e:
            print(workingdir + ' couldnt be deleted.\n', flush=True)
            print(e, flush=True)
            return 1





def executeOneInstance(PESTO_client, workingdir, resourcesdir, resultsdir, startingport, numberoftheVM, shareddrive, adminpassword, loglevel, username, userpassword):
    """
    executes an Instance
    waits till it terminates and returns
    """

    port = startingport + numberoftheVM
    INSTANCE = os.path.join(PESTO_client, 'PESTO-client\\Instance\\Instance.py')

    try:
        if username == "None":
            print('Executing Instance', flush=True)
            p = subprocess.Popen(['python', INSTANCE, workingdir, workingdir, resultsdir, resourcesdir, str(port), shareddrive, adminpassword, PESTO_client, loglevel])
        else:
            print('Executing Instance as '+ username + ' with password: '+ userpassword, flush=True)
            p = subprocess.Popen(['psexec.exe', '-n', '60', '-h', '/accepteula', '-u', username, '-p', userpassword, 'python', INSTANCE, workingdir, workingdir, resultsdir, resourcesdir, str(port), shareddrive, adminpassword, PESTO_client, loglevel],stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    except Exception as e:
        print('Error while executing instance. /returned/', flush=True)
        print(e, flush=True)
        return 1

    # wait process to terminate
    p.wait()
    print('Process returned: ', p.returncode, flush=True)
    return p.returncode




def executeInstances(PESTO_client, number_of_users,workingdir, resourcesdir, resultsdir, startingport, numberoftheVM, shareddrive, password, loglevel):
    """
    executes Instances
    wait till all terminates
    wihout h doesnt work from remote VM
    gives the connection 60 sec timeout.
    """

    Process = []

    for i in range(number_of_users):
        userworkingdir = workingdir + '\\MyUser'+str(i)
        port = startingport + (number_of_users*numberoftheVM) + i
        moreINSTANCEs = os.path.join(PESTO_client, 'PESTO-client\\Instance\\Instance.py')

        print('Executing instance as MyUser' + str(i), flush=True)
        try:
            P = subprocess.Popen(['psexec.exe','-n','60','-h','/accepteula','-u', "MyUser"+str(i) , '-p', 'redhat', 'python', moreINSTANCEs, workingdir, userworkingdir, resultsdir, resourcesdir, str(port),shareddrive,password, PESTO_client, loglevel], stdout=subprocess.PIPE, stderr= subprocess.PIPE)
            time.sleep(1)
        except Exception as e:
            print('Error while executing instance. /returned/',flush=True)
            print(e,flush=True)
            return 1
        Process.append(P)

    #wait processes to terminate
    for p in Process:
        p.wait()
    flag = 0
    for p in Process:
        print('Process on MyUser' + str(Process.index(p)) +' returned: ', p.returncode, flush=True)
        if p.returncode != 0:
            flag = 1
    print('All terminated\n',flush=True)
    return flag




def Create_User_Accounts(number_of_users):
    """
    creates windows users and adds them administrator rights
    """

    print('\n', flush=True)
    for i in range(number_of_users):
        print('Creating MyUser'+str(i)+' and giving it administrator rights.', flush=True)
        try:
            p = subprocess.Popen(['net', 'user', 'MyUser' + str(i), 'redhat', '/add'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout != b'':
                print(stdout.decode('utf-8'), flush=True)
            if stderr != b'':
                print(stderr.decode('utf-8'), flush=True)
        except Exception as e:
            print('Error creating user.\n', flush=True)
            print(e, flush=True)
            return 1

        try:
            p = subprocess.Popen(['net', 'localgroup','administrators', 'MyUser' + str(i), '/add'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout != b'':
                print(stdout.decode('utf-8'), flush=True)
            if stderr != b'':
                print(stderr.decode('utf-8'), flush=True)
        except Exception as e:
            print('Error giving administrator rights.\n', flush=True)
            print(e, flush=True)
            return 1

    return 0




def Delete_User_Accounts(number_of_users):
    """
    deletes the created users
    """

    for i in range(number_of_users):
        print('Deleting MyUser' + str(i) + '.', flush=True)
        try:
            p = subprocess.Popen(['net', 'user', 'MyUser' + str(i),'/delete'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout != b'':
                print(stdout.decode('utf-8') + '\n', flush=True)
            if stderr != b'':
                print(stderr.decode('utf-8') + '\n', flush=True)
        except Exception as e:
            print('Error occured while deleting the user /process continued/.\n', flush=True)
            print(e, flush=True)
            return 1
    return




def allowPorts(startingPort, numberofUsers, numberoftheVM):
    """
    creates new rules on the firewall for all ports
    """

    firstport = startingPort + (numberoftheVM * numberofUsers)
    lastport = firstport + numberofUsers - 1

    if numberofUsers == 1:
        ports = str(firstport)
    else:
        ports = str(firstport) + '-' + str(lastport)

    print('Enabling ports: ' + ports, flush=True)

    command = 'netsh advfirewall firewall add rule name="PESTO" dir=in action=allow protocol=TCP localport=' + ports
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout != b'':
            print(stdout.decode('utf-8') + '\n', flush=True)
        if stderr != b'':
            print(stderr.decode('utf-8') + '\n', flush=True)
    except Exception as e:
        print('Error occured while enabling ports.\n', flush=True)
        print(e, flush=True)
        return 1

    return 0




def deletePorts(startingPort, numberofUsers, numberoftheVM):
    """
    deletes ports
    """

    firstport = startingPort + (numberoftheVM * numberofUsers)
    lastport = firstport + numberofUsers - 1

    if numberofUsers == 1:
        ports = str(firstport)
    else:
        ports = str(firstport) + '-' + str(lastport)

    print('Deleting ports: ' + ports, flush=True)

    command = 'netsh advfirewall firewall delete rule name="PESTO" protocol=tcp localport=' + ports
    try:
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout != b'':
            print(stdout.decode('utf-8') + '\n', flush=True)
        if stderr != b'':
            print(stderr.decode('utf-8') + '\n', flush=True)
    except Exception as e:
        print(e, flush=True)

    return 0

def runCreateClients(PESTO_client, number_of_users, sharedDrive, resultsdir, workingdir, resourcesdir, numberoftheVM, startingport, password, loglevel, username, userpassword):
    if number_of_users == 1:

        #enabling ports
        retval = allowPorts(startingport, number_of_users, numberoftheVM)
        if retval == 1:
            input('Press Enter to continue..')
            return 1


        #creates working directory
        retval = createWorkingDirectory(workingdir)
        if retval != 0:
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        #executing the instance
        retval = executeOneInstance(PESTO_client, workingdir, resourcesdir, resultsdir, startingport, numberoftheVM, sharedDrive, password, loglevel, username, userpassword)
        if retval != 0:
            deleteWorkingDirectory(workingdir)
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        #deletes working directory
        retval = deleteWorkingDirectory(workingdir)
        if retval == 1:
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1


        #deletes ports
        deletePorts(startingport, number_of_users, numberoftheVM)

        input('ENTER')
        return 0

    else:
        #creates working directories for all users (workingdir\MyUserX)
        retval = createWorkingDirectories(workingdir, number_of_users)
        if retval == 1:
            input('Press Enter to continue..')
            return 1

        #enabling ports
        retval = allowPorts(startingport, number_of_users, numberoftheVM)
        if retval == 1:
            deleteWorkingDirectory(workingdir)
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        #creates windows users with admin rights
        retval = Create_User_Accounts(number_of_users)
        if retval != 0:
            deleteWorkingDirectory(workingdir)
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        retval = executeInstances(PESTO_client, number_of_users, workingdir, resourcesdir, resultsdir, startingPort, numberoftheVM, sharedDrive, password, loglevel)
        if retval != 0:
            Delete_User_Accounts(number_of_users)
            deleteWorkingDirectory(workingdir)
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        #deletes the created users
        retval = Delete_User_Accounts(number_of_users)
        if retval == 1:
            deleteWorkingDirectory(workingdir)
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        #deletes working directory
        retval = deleteWorkingDirectory(workingdir)
        if retval == 1:
            deletePorts(startingport, number_of_users, numberoftheVM)
            input('Press Enter to continue..')
            return 1

        # deletes ports
        deletePorts(startingport, number_of_users, numberoftheVM)


        input('ENTER')
        return 0

if __name__ == '__main__':
    number_of_users = int(sys.argv[1])
    ResultsDir = sys.argv[2]
    ResourcesDir = sys.argv[3]
    WorkingDir = sys.argv[4]
    numberoftheVM = int(sys.argv[5])
    sharedDrive = sys.argv[6]
    startingPort = int(sys.argv[7])
    password = sys.argv[8]
    loglevel = sys.argv[9]
    username = sys.argv[10]
    userpassword = sys.argv[11]


    PESTO_client = str.replace(sys.argv[0], r'PESTO-client\createClients\createClients.py', '')

    runCreateClients(PESTO_client, number_of_users, sharedDrive, ResultsDir, WorkingDir, ResourcesDir, numberoftheVM, startingPort, password, loglevel, username, userpassword)