import os
import shlex, subprocess

def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()

def executeSudoBash(bashCommand):
    process = subprocess.Popen(shlex.split(bashCommand), stdout=subprocess.PIPE)
    return process.communicate()

def getPID():
    bashCommand = "fuser 8000/tcp"
    return executeBash(bashCommand)

def stopWebApp(pid):
    bashCommand = ''

    if pid == None:
        bashCommand = "fuser -k 8000/tcp"
    else:
        bashCommand = "kill " + pid

    return executeBash(bashCommand)

if __name__ == '__main__':
    pid = getPID()[0].decode('utf-8').strip()
    stopWebApp()
