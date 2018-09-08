import boto3
import requests
from Trojan.settings import DEBUG

def getInstanceID():
    instance_id = 'i-0cb0d00c76e58046a'

    if not DEBUG:
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        instance_id = response.text

    return instance_id

def getVolumeID():
    instance_id = getInstanceID()

    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    volume_iterator = instance.volumes.all()
    volume_ids = [v.id for v in volume_iterator]

    return volume_ids[0]

def getDimension(namespace):
    dimensions_name = 'InstanceId'
    value = getInstanceID()

    if 'EBS' in namespace:
        dimensions_name = 'VolumeId'
        value = getVolumeID()
    elif 'ELB' in namespace:
        dimensions_name = 'LoadBalancer'
        pass

    return {'Name':dimensions_name,'Value':value}
