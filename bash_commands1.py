import os
import shlex, subprocess

def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()

def executeSudoBash(bashCommand):
    process = subprocess.Popen(shlex.split(bashCommand), stdout=subprocess.PIPE)
    return process.communicate()

def getPID():
    bashCommand = "fuser 8999/tcp"
    return executeBash(bashCommand)

if __name__ == '__main__':
    print(getPID())
