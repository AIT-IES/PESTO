"""
 --------------------------------------------------------------
 Copyright (c) 2017, AIT Austrian Institute of Technology GmbH.
 
 All rights reserved. See file PESTO _LICENSE for details.
 --------------------------------------------------------------


 PESTO-client\Instance\runSimulation.py

 checks the directories (workind, resources and results directories)
 cleans working directory
 copies containment of resources directory to working directory (and to a list)
 loads PESTO.json from working directory (was copied from resources directory if its necessary)
 adds new variables to system variables or appends new values to old ones
 executes task with working directory as "current working directory"
 copies results to the results directory
 cleanes working directory (again.)
 returns the return value of the executed task (or 100 in case of an error)
"""

import os
import logging
import glob
import shutil
import json
import subprocess
import distutils.dir_util
import time



def checkInputs(workingdir, resultsdir, resourcesdir):
    """
    checking inputs for existence
    """

    if ( False == os.path.isdir( workingdir )):
        logging.error("\n[ERROR] Working directory cant be found"+ workingdir)
        return 1

    if ( False == os.path.isdir( resultsdir )):
        logging.error("[ERROR] Results directory cant be found, "+ resultsdir)
        return 1

    if ( False == os.path.isdir( resourcesdir )):
        logging.error("[ERROR] Resources directory cant be found"+ resourcesdir)
        return 1

    return 0




def cleanWorkingDir( workingdir ):
    """
    cleans the working directory and checks if it was really cleaned
    """

    # Get all contents of the directory.
    contents = glob.glob( os.path.join( workingdir, '*' ) )

    # Delete all contents.
    for c in contents:
        if ( os.path.isfile( c ) ): os.remove( c )
        elif ( os.path.isdir( c ) ): shutil.rmtree( c )

    #without this line the directory wont be cleaned before the IF statement and it creates an error.
    contents = glob.glob( os.path.join( workingdir, '*' ) )

    if(contents == []):
        return 0
    else:
        logging.error("Working Directory couldnt be cleaned.")
        return 1




def setSystemVariables( jsonData ):
    """
    set system variables (f.e.: PATH)
    """

    if jsonData == []:
        logging.debug('No system variables will be changed\n')
        return 0

    #all data from json file
    for key in jsonData:
        for value in jsonData[key]:
            #if the keyword "key" is already an environment variable += can be used -> try block
            try:
                #separate with ;
                os.environ[key] += ";"
                #if "value" is already added it wont be again,
                #it must be checked after adding ";" otherwise for example: C:\ couldnt be added if C:\something\... is in the variable
                if os.environ[key].find(value+';') != -1:
                    #deletes ";"
                    if os.environ[key][len(os.environ[key]) - 1] == ';':
                        os.environ[key] = os.environ[key][:len(os.environ[key]) - 1]
                    break
                # add a new value to the environment variable "key"
                os.environ[key] += value
            #if keyword "key" doesnt exist += raises an error -> "key"  will be added to environment variables
            except:
                os.environ[key] = value
        logging.debug(key +': '+ str(os.environ[key]))

    return 0




def loadDataFromJSONFile(json_file):
    """
    open jsonfile and returns the contents
    """

    #check json file
    if ( False ==  os.path.isfile(json_file) ):
        logging.debug("No JSON file was found"+ json_file)
        return []

    #create directory from jason file
    with open(json_file, 'r') as outfile:
        try:
            json_data = json.load( outfile)
            logging.debug('Json file read.')
            return json_data
        except Exception as e:
            logging.error("JSON file is false formatted\n")
            logging.error(e)
            return 1



def executeTask(task, working_dir):
    """
    executes the task
    """

    # Run task
    logging.debug('START: '+ time.asctime( time.localtime(time.time()) ))
    print('START: '+ time.asctime( time.localtime(time.time()) ), flush=True)
    executable = os.path.join(working_dir, task)

    try:
        p = subprocess.Popen(executable, cwd=working_dir, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, universal_newlines=True)

        for line in p.stdout:
            print(line, flush=True)
            logging.debug(line)

        retval = None
        while retval == None:
            retval = p.poll()
        print('END: '+ time.asctime( time.localtime(time.time()) ), flush=True)
        logging.debug('END: '+ time.asctime( time.localtime(time.time()) ))
        return retval
    except Exception as e:
        logging.error('Error executing task.')
        logging.error(e)
        return 100




def copyResults( workingdir, resultsdir, pre_sim_file_list ):
    """
    copiing results from working directory to results directory
    """

    try:
        # Get complete list of contents from working directory.
        post_sim_file_list = distutils.dir_util.copy_tree( workingdir, workingdir, dry_run=1 )

        # List of relative file paths for files that where not previously copied (results).
        results_file_list = [ os.path.relpath( file, workingdir ) for file in post_sim_file_list if file not in pre_sim_file_list ]

        # Copy results files.
        distutils.dir_util.create_tree( resultsdir, results_file_list ) # Create directories.
        for file in results_file_list:
            shutil.copy( os.path.join( workingdir, file ), os.path.join( resultsdir, file ) )
        return 0
    except:
        logging.error("Error in copying the results")
        return 1


def runSimulation(workingdir, resultsdir, resourcesdir, task, jsonfile):

    #checking inputs (if the directories exist)
    retval = checkInputs(workingdir, resultsdir, resourcesdir)
    if retval == 1:
        return 100
    logging.debug('Directories checked.')

    #cleans the working directory
    retval = cleanWorkingDir(workingdir)
    if retval == 1:
        return 100
    logging.debug('Working directory cleaned.')

    # copy files from resources into working directory and to list pre_sim_file_list
    pre_sim_file_list = distutils.dir_util.copy_tree(resourcesdir, workingdir)
    logging.debug('Resources copied to working directory.')

    # get the data from the json file
    #check if there is a json file
    jsondata = loadDataFromJSONFile(jsonfile)
    if jsondata == 1:
        cleanWorkingDir(workingdir)
        return 100

    # set the system variables (like PATH)
    setSystemVariables(jsondata)

    # execute the simulation, if it cant be executed the working directory will be cleaned
    returnvalue = executeTask(task, workingdir)
    if returnvalue == 100:
        cleanWorkingDir(workingdir)
        return 100

    # save results in the results directory
    ret_val = copyResults(workingdir, resultsdir, pre_sim_file_list)
    if ret_val == 1:
        return 100
    logging.debug('Results saved in the results directory.\n')

    # clean working directory at the end
    cleanWorkingDir(workingdir)

    return returnvalue