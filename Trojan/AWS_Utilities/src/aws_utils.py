import boto3
import requests

def getInstanceID():
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text

    return instance_id, {'instance_id':instance_id}

def getInstanceName(instance_id):
    ec2 = boto3.resource('ec2')
    
