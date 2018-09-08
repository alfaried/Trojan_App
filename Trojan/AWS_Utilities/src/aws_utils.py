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

def getLoadBalancerIDs(type=None):
    client = boto3.client('elbv2')
    loadbalancers = client.describe_load_balancers()

    if len(loadbalancers['LoadBalancers']) == 0:
        raise Exception('No load balancers configured')

    loadbalancer_ids = []

    if type == None:
        loadbalancer_ids = [lb['LoadBalancerArn'] for lb in loadbalancers['LoadBalancers']]

    for lb in loadbalancers['LoadBalancers']:
        if lb['Type'] == type:
            loadbalancer_ids.append(lb['LoadBalancerArn'])

    return loadbalancer_ids

def getLoadBalancerNames():
    client = boto3.client('elb')
    loadbalancers = client.describe_load_balancers()

    if len(loadbalancers['LoadBalancerDescriptions']) == 0:
        raise Exception('No load balancers configured')

    loadbalancer_names = [lb['LoadBalancerName'] for lb in loadbalancers['LoadBalancerDescriptions']]
    return loadbalancer_names

def getDimension(namespace):
    dimensions_name = 'InstanceId'
    value = getInstanceID()

    if 'EBS' in namespace:
        dimensions_name = 'VolumeId'
        value = getVolumeID()
    elif 'ELB' in namespace:
        dimensions_name = 'LoadBalancer'

        if 'Application' in namespace:
            lb_ids = getLoadBalancerID('application')[0]
            tmp = lb_ids.split(':')[-1].split('/')
            value = tmp[1] + '/' + tmp[2] + '/' + tmp[3]

        elif 'Network' in namespace:
            lb_ids = getLoadBalancerID('network')[0]
            tmp = lb_ids.split(':')[-1].split('/')
            value = tmp[1] + '/' + tmp[2] + '/' + tmp[3]

        else:
            dimensions_name = 'LoadBalancerName'
            value = getLoadBalancerNames()[0]

    return {'Name':dimensions_name,'Value':value}

def getAllRunningInstance():
    instances = {}
    client = boto3.client('ec2')
    results = client.describe_instances()

    return instances

def getAllLoadBalancers():
    loadbalancers = {}
    client = boto3.client('elb')
    loadbaresultslancers = client.describe_load_balancers()

    return loadbalancers

def getAllLoadBalancersV2():
    loadbalancersV2 = {}
    client = boto3.client('elbv2')
    results = client.describe_load_balancers()
    
    return loadbalancersV2
