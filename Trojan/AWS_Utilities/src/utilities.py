import boto3
import hashlib
import requests
from AWS_Utilities.src import config, server_util
from Trojan.settings import DEBUG, ACCOUNT_SECRET_KEY

def hashPlainText(plaintext):
    plaintext_byte = plaintext.encode('utf-8')
    hashedtext = hashlib.sha256(plaintext_byte).hexdigest()
    return hashedtext

def validate(secret_key):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    if secret_key == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify a secret_key to access information'
        return False,response

    if hashPlainText(secret_key) != ACCOUNT_SECRET_KEY:
        response['HTTPStatus'] = 'Unauthorized'
        response['HTTPStatusCode'] = '401'
        response['Message'] = 'Please enter a valid secret_key'
        return False,response

    return True,response

def getOwnerID():
    client = boto3.client('sts')
    account = client.get_caller_identity()

    return account['Account']

def getInstanceID():
    instance_id = 'i-0cb0d00c76e58046a'

    if not DEBUG:
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
        instance_id = response.text

    return instance_id

def getVolumeIDs(instance_id=None):
    if instance_id == None:
        instance_id = getInstanceID()

    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)
    volume_iterator = instance.volumes.all()
    volume_ids = [v.id for v in volume_iterator]

    return volume_ids

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
        value = getVolumeIDs()[0]
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

def getAllInstances():
    instances = {'Active':{},'Non-Active':{}}
    client = boto3.client('ec2')
    results = client.describe_instances()

    active_instance_count = 0
    non_active_instance_count = 0

    active_instance_list = []
    non_active_instance_list = []

    for instance in results['Reservations']:
        for i in instance['Instances']:
            if i['State']['Name'] == 'running':
                active_instance_count += 1
                active_instance_list.append(
                    {
                        'Instance_ID':i['InstanceId'],
                        'ImageId':i['ImageId'],
                        'Volume_IDs':getVolumeIDs(i['InstanceId']),
                        'PublicIpAddress':i['PublicIpAddress'],
                        'PublicDnsName':i['PublicDnsName'],
                    }
                )
            elif not i['State']['Name'] == 'terminated':
                non_active_instance_count += 1
                non_active_instance_list.append(
                    {
                        'Instance_ID':i['InstanceId'],
                        'ImageId':i['ImageId'],
                        'Volume_IDs':getVolumeIDs(i['InstanceId']),
                        'PublicIpAddress':i['PublicIpAddress'],
                        'PublicDnsName':i['PublicDnsName'],
                    }
                )

    instances['Active'].update({'Count':active_instance_count,'Details':active_instance_list})
    instances['Non-Active'].update({'Count':non_active_instance_count,'Details':non_active_instance_list})

    return instances

def getAllLoadBalancers():
    loadbalancers = {'Classic_ELB':{}}
    client = boto3.client('elb')
    results = client.describe_load_balancers()

    celb_count = 0
    celb_list = []

    for lb in results['LoadBalancerDescriptions']:
        celb_count += 1
        celb_list.append(
            {
                'LoadBalancerName':lb['LoadBalancerName'],
                'DNSName':lb['DNSName'],
            }
        )

    loadbalancers['Classic_ELB'].update({'Count':celb_count,'Detials':celb_list})

    return loadbalancers

def getAllLoadBalancersV2():
    loadbalancersV2 = {'Application_ELB':{},'Network_ELB':{}}
    client = boto3.client('elbv2')
    results = client.describe_load_balancers()

    aelb_count = 0
    nelb_count = 0

    aelb_list = []
    nelb_list = []

    for lb in results['LoadBalancers']:
        if lb['Type'] == 'application':
            aelb_count += 1
            aelb_list.append(
                {
                    'LoadBalancerArn':lb['LoadBalancerArn'],
                    'LoadBalancerName':lb['LoadBalancerName'],
                    'DNSName':lb['DNSName'],
                }
            )
        if lb['Type'] == 'network':
            nelb_count += 1
            nelb_list.append(
                {
                    'LoadBalancerArn':lb['LoadBalancerArn'],
                    'LoadBalancerName':lb['LoadBalancerName'],
                    'DNSName':lb['DNSName'],
                }
            )

    loadbalancersV2['Application_ELB'].update({'Count':aelb_count,'Details':aelb_list})
    loadbalancersV2['Network_ELB'].update({'Count':nelb_count,'Details':nelb_list})

    return loadbalancersV2

def getAllVolumes():
    volumes = {'Volumes':{}}

    count = 0
    list = []

    client = boto3.client('ec2')
    results = client.describe_volumes()

    for volume in results['Volumes']:
        count += 1

        instance_list = []
        for attachment in volume['Attachments']:
            instance_list.append(attachment['InstanceId'])

        list.append(
            {
                'VolumeID':volume['VolumeId'],
                'Size':volume['Size'],
                'Attachements':instance_list
            }
        )

    volumes['Volumes'].update({'Count':count,'Details':list})

    return volumes

def getAllElasticIPs():
    elastic_ips = {'Elastic_IPs':{}}

    elastic_ips_assigned = getElasticIPs_Assigned()
    elastic_ips_unassgined = getElasticIPs_Unassigned()

    elastic_ips['Elastic_IPs']['Assgined'] = elastic_ips_assigned['Elastic_IPs']
    elastic_ips['Elastic_IPs']['Unassgined'] = elastic_ips_unassgined['Elastic_IPs']

    return elastic_ips

def getElasticIPs_Assigned():
    elastic_ips = {'Elastic_IPs':{}}

    list = []

    client = boto3.client('ec2')
    results = client.describe_addresses()

    for ips in results['Addresses']:
        try:
            list.append(
                {
                    'InstanceId':ips['InstanceId'],
                    'PublicIp':ips['PublicIp'],
                    'Domain':ips['Domain'],
                }
            )
        except:
            pass

    elastic_ips['Elastic_IPs'] = list

    return elastic_ips

def getElasticIPs_Unassigned():
    elastic_ips = {'Elastic_IPs':{}}

    list = []

    client = boto3.client('ec2')
    results = client.describe_addresses()

    for ips in results['Addresses']:
        try:
            ips['InstanceId']
        except:
            list.append(
                {
                    'PublicIp':ips['PublicIp'],
                    'AllocationId':ips['AllocationId'],
                }
            )

    elastic_ips['Elastic_IPs'] = list

    return elastic_ips

def getAllSnapshots():
    snapshots = {'Snapshots':{}}

    owner_id = getOwnerID()

    snapshots_count = 0
    snapshots_list = []

    client = boto3.client('ec2')
    results = client.describe_snapshots(
        OwnerIds=[
            owner_id,
        ],
    )

    for snapshot in results['Snapshots']:
        snapshots_count += 1
        snapshots_list.append(
            {
                'SnapshotId':snapshot['SnapshotId'],
                'State':snapshot['State'],
                'Attached_Volume':snapshot['VolumeId'],
                'Description':snapshot['Description'],
            }
        )

    snapshots['Snapshots'].update({'Count':snapshots_count,'Details':snapshots_list})

    return snapshots

def getAllImages():
    images = {'Images':{}}

    owner_id = getOwnerID()

    images_count = 0
    images_list = []

    client = boto3.client('ec2')
    results = client.describe_images(
        Owners=[
            owner_id,
        ],
    )

    for image in results['Images']:
        images_count += 1
        images_list.append(
            {
                'ImageId':image['ImageId'],
                'ImageType':image['ImageType'],
                'Platform':image['Platform'],
                'State':image['State'],
                'Description':image['Description'],
                'Name':image['Name'],
            }
        )

    images['Images'].update({'Count':images_count,'Details':images_list})

    return images

def getCredentials():
    results = {'State':'Development','Results':'Not Available'}

    if not DEBUG:
        file_path_credentials = config.AWS_CREDENTIALS_FILE
        file_path_config = config.AWS_CONFIG_FILE
        results['State'] = 'Production'
        results_dict = {}

        with open(file_path_credentials,'r') as file_output:
            file_output.readline()
            for line in file_output.readlines():
                results_dict.update({line.split('=')[0]:line.split('=')[1].strip()})

        with open(file_path_config,'r') as file_output:
            file_output.readline()
            for line in file_output.readlines():
                results_dict.update({line.split('=')[0]:line.split('=')[1].strip()})

        results['Results'] = results_dict

    return results

def getPublicKey():
    results = {'State':'Development','Results':'Not Available'}

    if not DEBUG:
        file_path_keys = config.SSH_KEYS_FILE
        results['State'] = 'Production'
        results_dict = []

        with open(file_path_keys,'r') as file_output:
            file_output.readline()
            for line in file_output.readlines():
                if 'ssh-rsa' in line:
                    results_dict.append(line)

        results['Results'] = results_dict

    return results

def addPublicKey(public_key=None):
    results = {'State':'Development','Status':'Unsuccessful'}

    if not DEBUG:
        if 'ssh-rsa' not in public_key:
            public_key = 'ssh-rsa ' + public_key

        pk_dir = config.SSH_KEYS_FILE
        server_util.addPublicKey(public_key,pk_dir)

        results = {'State':'Production','Status':'Successful'}

    return results

def addAWSCredentials(access_key,secret_access_key,region_name,output_file):
    if not DEBUG:
        file_path_credentials = config.AWS_CREDENTIALS_FILE
        file_path_config = config.AWS_CONFIG_FILE

        server_util.addAWSCredentials(access_key,secret_access_key)
        server_util.addAWSConfig(region_name,output_file)
