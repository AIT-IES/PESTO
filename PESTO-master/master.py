"""
 --------------------------------------------------------------
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.
 
 All rights reserved. See file PESTO _LICENSE for details.
 --------------------------------------------------------------

 PESTO-master\master.py

 STARTS PESTO
 reads settings from the .json file
 check resources directory (and the shared drive with it)
 creates a logfile logfile_master.log and saves it to te resources directory (or to PESTO-master)
 checks all client computers
 kills processes on clients started with PsExec
 creates results directory
 creates PESTO.json in results directory with the system variables to be changed
 executes PESTO-client\createClients\createClients.py on all clients
 starts PESTO-master\server.py
 waits until server finished and returns
 """


import logging
import server
import os
import time
import sys
import subprocess
import shutil
import json




def startLogging(VMs):
    """
    deletes old logfile
    creates new logfile and starts the logging process
    """

    path = str.replace(sys.argv[0], 'master.py', 'logfile_master.log')

    if os.path.isfile(path):
        try:
            os.remove(path)
        except:
            print(path + ' couldnt be deleted.\n')

    logging.basicConfig(filename=path, level= logging.INFO, format='%(levelname)s:%(message)s')

    # logs starting time and clients
    logging.info(str(time.asctime(time.localtime(time.time()))))
    logging.info('List of VMs: ' + str(VMs)+'\n')




def copyLogfile(resultsdir):
    """
    copies the master-logfile to the results directory
    in case, the results directory cant be accessed, the master-logfile will be copied to PESTO-master with the name logfile_master_TIME
    """

    src = str.replace(sys.argv[0], 'master.py', 'logfile_master.log')
    dst = resultsdir + '\\logfile_master.log'

    try:
        shutil.copyfile(src, dst)
    except:
        print('Cant copy master-logfile to: ',resultsdir)
        dst = str.replace(sys.argv[0], 'master.py', 'logfile_master' + str(int(time.time())) + '.log')
        print('Copy to: ', dst)
        shutil.copyfile(src, dst)




def startServer(VMs, number_of_users, tasklist, startingPort):
    """
    starts the server
    """

    server.Server(VMs, number_of_users, tasklist, startingPort)




def remoteExecution(PESTO_client, VMs, number_of_users, startingPort, WorkingDirectory, ResourcesDirectory, ResultsDirectory, sharedDrive, adminpassword, loglevel, username, userpassword):
    """
    runs all  processes
    with the flag /savecred the program will ask for (master)administrator password only 1 time.
    -n 30 gives the connection 30 sec timeout
    """

    if number_of_users >= 1:
        for VM in VMs:
            logging.info('Executing clients on: ' + VM)
            clientcreator = os.path.join(PESTO_client, 'PESTO-client\\createClients\\createClients.py')
            command = 'runas /savecred /user:administrator "psexec.exe \\\\'+ VM +' -n 30 /accepteula -u administrator -p ' + adminpassword + ' python '+clientcreator+' '+str(number_of_users)+' '+ResultsDirectory+' '+ResourcesDirectory+' '+WorkingDirectory+' '+str(VMs.index(VM))+' '+sharedDrive+' '+str(startingPort)+' '+adminpassword+' '+loglevel+' '+username+' '+userpassword+'"'
            try:
                p = subprocess.Popen(command, stdout= subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if stdout != b'':
                    logging.info('Stdout: '+ stdout.decode('utf-8'))
                if stderr != b'':
                    logging.info('Stderr: '+ stderr.decode('utf-8'))
                logging.info('Returncode: ' + str(p.returncode))
                return p.returncode
            except Exception as e:
                logging.error('Error in execution.')
                logging.error(e)
                return 1
    else:
        logging.error('Wrong parameter: number_of_users -> '+ str(number_of_users))
        print('Wrong parameter: number_of_users -> '+ str(number_of_users))
        return 1




def checkResourcesdir(resourcesdir):
    """
    checks resourcesdir
    """

    if not os.path.isdir(resourcesdir):
        print('Resources directory '+resourcesdir+ ' cant be found.')
        return 1
    return 0




def checkVMs(VMs):
    """
    checks if clients can be pinged
    """

    for VM in VMs:
        p = subprocess.Popen(['ping', '-n', '1', VM], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if stdout != b'':
            logging.info(stdout.decode('utf-8'))
        if stderr != b'':
            logging.info(stderr.decode('utf-8'))
        if p.returncode != 0:
            print('Computer: ' +VM+ ' cant be pinged.')
            logging.error('Computer: ' +VM+ ' cant be pinged.')
            return 1

    return 0


def runMaster(PESTO_client, VMs, tasklist, workingdir, resourcesdir, resultsdir, shareddrive, adminpassword, number_of_users, startingPort, loglevel, username, userpassword):

    retval = remoteExecution(PESTO_client, VMs, number_of_users, startingPort, workingdir, resourcesdir, resultsdir, shareddrive, adminpassword, loglevel, username, userpassword)
    if retval == 1:
        print('Error executing PsExec.')
        return 1

    startServer(VMs, number_of_users, tasklist, startingPort)

    logging.info('master finished\n')

    copyLogfile(resultsdir)


def usage():
    print('USAGE:\n')
    print('master.py <settings.json>\n')
    print('Read wiki: https://github.com/AIT-IES/PESTO/wiki')




def createResultsDirectory(resultsdir):
    """
    creates results directory if it doesnt exists
    """

    if not os.path.isdir(resultsdir):
        print('Creating: ' + resultsdir)
        try:
            os.makedirs(resultsdir)
        except Exception as e:
            print('Error creating the working directory\n')
            print(e)
            return 1
        return 0




def readSettings(file):
    """
    reads the .json file
    calls checkresourcesdirectory, killAll, writeSystemVariablesFile and createResultsdir
    """

    print("Reading settings")
    try:
        settingsfile = open(file, 'r')
    except Exception as e:
        print('File ' + file + ' cant be opened.')
        print(e)
        return 1

    try:
        settings = json.load(settingsfile)
    except Exception as e:
        print('Settings file false formatted.')
        print(e)
        return 1

    try:
        PESTO_client = settings["pesto-client_path"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        clients = settings["clients"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        workingdir = settings["working directory"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        resourcesdir = settings["resources directory"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        resultsdir = settings["results directory"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        shareddrive = settings["shared drive"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        adminpassword = settings["adminpassword"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        tasks = settings["tasks"]
    except Exception as e:
        print('No keyword found: ',e)
        return 1

    try:
        system_variables = settings["system variables"]
    except:
        print('System variables wont be changed')
        system_variables = None

    try:
        windows_users = int(settings["windows users"])
    except:
        windows_users = 1

    try:
        port = int(settings["port"])
    except:
        port = 50000

    try:
        loglevel = settings["loglevel"]
        if loglevel.lower() == "info":
            loglevel = "info"
        elif loglevel.lower() == "debug":
            loglevel = "debug"
        else:
            loglevel = "info"
    except:
        loglevel = "info"

    try:
        username = settings["user"][0]
        userpassword = settings["user"][1]
    except:
        username = "None"
        userpassword = "None"

    results = os.path.join(shareddrive, resultsdir)
    resources = os.path.join(shareddrive, resourcesdir)

    retval = checkResourcesdir(resources)
    if retval == 1:
        return 1

    startLogging(clients)

    retval = checkVMs(clients)
    if retval == 1:
        return 1

    killAll(clients, adminpassword)

    retval = createResultsDirectory(results)
    if retval == 1:
        return 1

    if system_variables != None:
        retval = createSystemVariablesFile(system_variables, resources)
        if retval == 1:
            return 1


    return PESTO_client, clients, workingdir, resources, results, shareddrive, adminpassword, tasks, windows_users, port, loglevel, username, userpassword




def killAll(clients, adminpassword):
    """
    calls PsKill to kill all processes and underprocesses started by PsExec on the clients
    """

    for client in clients:
        command = 'runas /savecred /user:administrator "pskill /accepteula -t \\\\'+ client +' -u administrator -p '+ adminpassword +' PSEXESVC"'
        try:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            time.sleep(1)
        except Exception as e:
            print('Error in execution.')
            print(e)
            return 1




def createSystemVariablesFile(SystemVariables, resourcesdir):
    """
    reads section "system variables" from .json file and writes it in a file (PESTO.json) to the resources directory
    """

    file = resourcesdir + '\\PESTO.json'
    try:
        sysvarfile = open(file, 'w')
    except Exception as e:
        print('File ' + file + ' cant be opened.')
        print('System Variables cant be changed')
        print(e)
        return 1
    try:
        json.dump(SystemVariables, sysvarfile)
    except Exception as e:
        print(e)
        sysvarfile.close()
        return 1

    sysvarfile.close()

def main():

    if len(sys.argv) == 2:

        settingsfile =  sys.argv[1]

        list = readSettings(settingsfile)

        if list != 1:
            PESTO_client, clients, workingdir, resources, results, shareddrive, adminpassword, tasks, windows_users, port, loglevel, username, userpassword = list
            runMaster(PESTO_client, clients, tasks, workingdir, resources, results, shareddrive, adminpassword, windows_users, port, loglevel, username, userpassword)

    else:

        usage()

main()