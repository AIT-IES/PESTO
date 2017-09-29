"""
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.
 
 All rights reserved. See file PESTO _LICENSE for details.



PESTO-client\Instance\Instance.py

 creates a logfile with logfile_HOSTNAME_USERNAME.log in results directory
 connects user to the shared drive
 creates socket and connects to PESTO-master\server.py
 receives task from server.py
 starts PESTO-client\Instance\runSimulation.py and passes the task to it
 after the last tasks disconnects from shared drive and returns

"""



import time
import sys
import getpass
import socket
import logging
import os
import subprocess
import runSimulation


class Instance:

    def __init__(self, port, workingdir, userworkingdir, shareddrive, resultsdir, resourcesdir, password, PESTO_client, loglevel):
        #connection to shared drive
        retval = self.connectSharedDrive(shareddrive, password, resourcesdir)
        if retval == 1:
            return
        elif retval == 2:
            if not os.path.isdir(resourcesdir):
                return

        # starts logging
        self.startLogging(loglevel, resultsdir)

        #asks ip of client
        ip = socket.gethostname()

        #creates a socket s
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except Exception as e:
            logging.error('Error creating socket')
            logging.error(e)
            self.disconnect_from_shared_drive(shareddrive)
            return

        logging.debug('Bind to port: ' + str(port))
        print('Bind to port: ' + str(port), flush=True)
        #binding to port
        try:
            s.bind((ip, port))
        except Exception as e:
            logging.error(str(e))
            print(e, flush=True)
            logging.error('Error at binding to port /returned/')
            self.disconnect_from_shared_drive(shareddrive)
            return

        logging.debug('Listen on port: ' + str(port))
        #listening on port
        try:
            s.listen()
        except Exception as e:
            logging.error('Error while listening')
            print(e, flush=True)
            logging.error(e)
            self.disconnect_from_shared_drive(shareddrive)
            return

        #accepts connection (with a timeout of 60 sec)
        #sends the "Ready" message (master knows its ready to use)
        #receives tasks and calls receive_command
        #copies the logfile after all tasks
        while True:
            s.settimeout(60)
            try:
                conn, addr = s.accept()
            except Exception as e:
                logging.error('Error at port: '+ str(port))
                print(e, flush=True)
                logging.error(e)
                self.disconnect_from_shared_drive(shareddrive)
                return
            logging.info('connect to -'+str(addr))
            print('connect to -' + str(addr), flush=True)
            conn.sendall(str.encode("Ready"))
            while True:
                flag = self.Recieve_command(conn, workingdir, userworkingdir, resultsdir, resourcesdir)
                if flag == 1:
                    self.disconnect_from_shared_drive(shareddrive)
                    return




    def startLogging(self, loglevel, resultsdir):

        """
        creates new logfile in the directory PESTO-client\LOGFILES
        """
        hostname = socket.gethostname()
        username = getpass.getuser()
        path = resultsdir + '\\logfile_' + hostname + '_' + username + '.log'

        if os.path.isfile(path):
            try:
                os.remove(path)
            except:
                pass

        if loglevel == "info":
            level = logging.INFO
        else:
            level = logging.DEBUG

        logging.basicConfig(filename=path,
                            level=level,
                            format='%(levelname)s:%(message)s')

        logging.debug(str(time.asctime(time.localtime(time.time()))))
        logging.debug('Start Instance on ' + hostname + ', ' + username + '\n')




    def connectSharedDrive(self, shareddrive, password, resourcesdir):
        """
        connects to shared drive
        """

        print('Connecting to shared drive: ' + shareddrive, flush=True)

        if os.path.isdir(resourcesdir):
            print('Already connected', flush=True)
            return 0

        try:
            p = subprocess.Popen(['net', 'use', shareddrive, '/user:administrator', password],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stdout != b'':
                print(stdout.decode('utf-8') + '\n', flush=True)
            if stderr != b'':
                print(stderr.decode('utf-8') + '\n', flush=True)
                return 2
        except Exception as e:
            print('Error occured while connecting /returned/.\n', flush=True)
            print(e, flush=True)
            return 1
        return 0




    def disconnect_from_shared_drive(self, shareddrive):
        """
        disconnects from the shared drive
        """

        print('Disconnecting from shared drive', flush=True)
        starttime = time.time()
        while True:
            if time.time() > starttime + 2:
                return 1

            try:
                p = subprocess.Popen(['net', 'use', shareddrive, '/del'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = p.communicate()
                if stdout != b'':
                    print(stdout.decode('utf-8') + '\n', flush=True)
                if stderr != b'':
                    print(stderr.decode('utf-8') + '\n', flush=True)
                if p.returncode == 0:
                    return
                else:
                    time.sleep(1)
            except Exception as e:
                print('Error occured while disconnecting.\n', flush=True)
                print(e, flush= True)
                return 1





    def Recieve_command(self, conn, workingdir, userworkingdir, resultsdir, resourcesdir):
        """
        reads data from socket
        converts it into a string
        calls task with runSimulation
        after simulation ends, sends "Ready" -> ready for next task
        """

        try:
            data = conn.recv(1024)
        except:
            logging.debug('No more tasks.')
            print('No more tasks', flush=True)
            return 1

        task = data.decode('utf-8')

        if task == '':
            return 1

        logging.info('Recieved task:\n' + task + '\n')
        print('Recieved task:\n' + task + '\n', flush=True)

        self.executeTask(task, workingdir, userworkingdir, resultsdir, resourcesdir)

        try:
            conn.sendall(str.encode("Ready"))
        except Exception as e:
            print(e, flush=True)
            return 1

        return 0




    def executeTask(self, task, workingdir, userworkingdir, resultsdir, resourcesdir):
        """
        calls the runSimulation module to execute the task
        runSimulation returns a value, 100 if somthing went wrong while copying files etc.. otherwise the returnvalue of the simulation
        the simulation should return 0 or it will be taken as a task with error
        """

        logging.debug('Run simulation:\n')
        jsonfile = userworkingdir + '\\PESTO.json'

        if workingdir != userworkingdir:
            task = str.replace(task, workingdir, userworkingdir)
        logging.debug(task)

        retval = runSimulation.runSimulation(userworkingdir, resultsdir, resourcesdir, task, jsonfile)
        logging.info('Return value of the simulation: ' + str(retval) + '\n')
        print('Return value of the simulation: ' + str(retval) + '\n', flush=True)

        if workingdir != userworkingdir:
            task = str.replace(task, userworkingdir, workingdir)

        if retval != 0:
            failurefile = open(resultsdir + '\\tasks_error_in_execution.txt', 'a')
            failurefile.write(task+'\n')
            failurefile.close()


if __name__ == '__main__':
    workingdir = sys.argv[1]
    userworkingdir = sys.argv[2]
    resultsdir = sys.argv[3]
    resourcesdir = sys.argv[4]
    port = int(sys.argv[5])
    shareddrive = sys.argv[6]
    password = sys.argv[7]
    PESTO_client = sys.argv[8]
    loglevel = sys.argv[9]

    Instance(port, workingdir, userworkingdir, shareddrive, resultsdir, resourcesdir, password, PESTO_client, loglevel)