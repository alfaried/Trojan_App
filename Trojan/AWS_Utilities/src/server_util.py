import os
import shlex, subprocess

# Return output : tuple, error : default-None
def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()

def changeFilePermission(permission,filepath):
    return False
