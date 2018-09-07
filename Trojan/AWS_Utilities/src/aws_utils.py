import boto3
import requests

def getCurrentInstanceID():
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text

    return instance_id
