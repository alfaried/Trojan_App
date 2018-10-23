import ipgetter
import shlex, subprocess

def executeBash(bashCommand):
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    return process.communicate()

def curlURL(ip_address):
    bashCommand = 'curl http://' + ip_address + ':8999/event/recovery/send_information/'
    # bashCommand = 'curl http://' + ip_address + ':8999/'
    return executeBash(bashCommand)

if __name__ == '__main__':
    curlURL(ipgetter.myip())
