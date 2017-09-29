"""
 --------------------------------------------------------------
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.

 All rights reserved. See file PESTO _LICENSE for details.
 --------------------------------------------------------------

 PESTO-master\server.py

 creates two lists, ports and ips
 creates connection with all clients using sockets
 sends task to the first client in the list without a task
 waits all clients and returns
"""

import logging
import time
import socket
import select

class Server:

    def __init__(self, VMs, number_of_users, tasks, startingPort):
        """
        starts server process
        """

        logging.info('Server started')
        print('Start server')
        IPs, Ports = self.Ports_and_IPs(VMs, number_of_users, startingPort)
        if len(IPs) != len(Ports):
            logging.error('Error in IPs or Ports. /server returned/')
            print('Error in IPs or Ports.')
            return

        Workers = self.create_Sockets(IPs, Ports)
        if len(Workers) < len(IPs):
            logging.error('Number of cleints is less then expected. /server returned/')
            print('Less clients then expected')
            return

        self.sendTasks(Workers, tasks)
        return




    def findWorker(self, task, Workers):
        """
        looking for "non-working" clients
        sends the task for the first free client
        """

        sread = []

        while sread == []:
            # creates a list (sread) with the free Workers
            # (if task is complete worker sends a word back -> worker is readable, worker is ready to new task)
            (sread, swrite, serr) = select.select(Workers, [], [])

        # takes the first ready worker from list sread,
        # reads the data the worker sent
        # sends the job for the worker and returns
        for worker in sread:
            try:
                data = worker.recv(1024).decode('utf-8')
            except Exception as e:
                logging.warning('Problem at reading reply msg from ' + str(worker))
                logging.error(e)
                return 1
            try:
                worker.sendall(str.encode(task))
                logging.info('Sending task:\t' + task + '\nto:\t' + str(worker) )
            except Exception as e:
                logging.warning('Problems sending ' + task + ' to ' + str(worker))
                logging.error(e)
                return 1
            return 0




    def sendTasks(self, Workers, tasks):
        """
        sends tasks to findWorker
        """

        i = 0
        for task in tasks:
            retval = self.findWorker(task, Workers)
            if retval != 0:
                logging.error('/Server returned/')
                return
            i = i + 1
            print('\nSending task ' + str(i) + '/' + str(len(tasks)) + '  '+ time.asctime(time.localtime(time.time())) + '\n', task)

        #wait until all clients are ready
        sread = []
        while len(sread) != len(Workers):
            (sread, swrite, serr) = select.select(Workers, [], [])




    def create_Sockets(self, IPs, Ports):
        """
        connects to the clients(60 sec timeout for each)
        returns all the "Workers"
        """

        Workers = []
        for i in range(len(IPs)):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except Exception as e:
                logging.error('Error creating socket')
                logging.error(e)
                return Workers
            starttime = time.time()
            while True:
                try:
                    s.connect((IPs[i], int(Ports[i])))
                    break
                except:
                    if time.time() >= starttime + 60:
                        logging.warning('Timeout while waiting for: '+ IPs[i] + ':' + str(Ports[i]))
                        return Workers

                    time.sleep(1)
                    pass
            print('Connected to - ' + IPs[i] + ':' + str(Ports[i]))
            logging.info('Connected to - ' + IPs[i] + ':' + str(Ports[i]))
            Workers.append(s)

        logging.info('Connected to available clients')
        return Workers




    def Ports_and_IPs(self, VMs, number_of_users, startingPort):
        """
        creates two lists, IPs and Ports
        """

        Ports = []
        IPs = []
        port = startingPort
        for VM in VMs:
            for i in range(number_of_users):
                Ports.append(port)
                IPs.append(VM)
                port = port + 1
        return IPs, Ports
