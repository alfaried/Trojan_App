import os
import shlex, subprocess

# Return output : tuple, error : default-None
def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()

def executeSudoBash(bashCommand):
    process = subprocess.Popen(shlex.split(bashCommand), stdout=subprocess.PIPE)
    return process.communicate()

def addPublicKeyToFile(public_key,filepath):
    bashCommand = 'sudo bash -c "echo ' + public_key + ' >> ' + filepath + '"'
    return executeSudoBash(bashCommand)

def addAWSCredentialsToFile(access_key,secret_access_key,filepath):
    # User profile
    bashCommand = 'sudo bash -c "echo [deafult] >> ' + filepath + '"'
    executeSudoBash(bashCommand)

    # Access Key
    bashCommand = 'sudo bash -c "echo ' + access_key + ' > ' + filepath + '"'
    executeSudoBash(bashCommand)

    # Secret Access Key
    bashCommand = 'sudo bash -c "echo ' + secret_access_key + ' > ' + filepath + '"'
    executeSudoBash(bashCommand)

def addAWSConfigToFile(region_name,output_format,filepath):
    # User profile
    bashCommand = 'sudo bash -c "echo [deafult] >> ' + filepath + '"'
    executeSudoBash(bashCommand)

    # Region Name
    bashCommand = 'sudo bash -c "echo ' + region_name + ' > ' + filepath + '"'
    executeSudoBash(bashCommand)

    # Output File Format
    bashCommand = 'sudo bash -c "echo ' + output_format + ' > ' + filepath + '"'
    executeSudoBash(bashCommand)
