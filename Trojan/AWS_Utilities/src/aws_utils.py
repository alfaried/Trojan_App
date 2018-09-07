import boto3
import requests

def getInstanceID():
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text

    return instance_id

def getVolumeID():
    instance_id = getInstanceID()

    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    volumes = instance.volumes.all()

    return volumes[0]
