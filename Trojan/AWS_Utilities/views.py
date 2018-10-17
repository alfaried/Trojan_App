import os
import boto3
import traceback
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.utilities import *
from botocore.exceptions import ClientError


# Request:
#
def test(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}
    return JsonResponse(response)

# Request:
# - secret_key
#
def account_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200, 'User':{}}

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    try:
        client = boto3.client('sts')
        account = client.get_caller_identity()

        response['User'].update({'Account':account['Account']})
        response['User'].update({'Arn':account['Arn']})
        response['User'].update({'UserId':account['UserId']})

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    response['User'].update(getCredentials())
    return JsonResponse(response)

# Request:
# - access_key
# - secret_access_key
# - secret_key
#
def account_updateAWSCredentials(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200, 'User':{}}

    access_key = request.GET.get('access_key').replace(' ','+')
    secret_access_key = request.GET.get('secret_access_key').replace(' ','+')
    if access_key == None or secret_access_key == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify a access_key and a secret_access_key'
        return JsonResponse(response)

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    region_name = 'ap-southeast-1' if request.GET.get('region_name') == None else request.GET.get('region_name')
    output_file = 'json' if request.GET.get('output_file') == None else request.GET.get('output_file')

    try:
        addAWSCredentials(access_key,secret_access_key,region_name,output_file)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    response['User'].update(getCredentials())
    return JsonResponse(response)

# Request:
# - secret_key
# - public_key
#
def account_addPublicKey(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    public_key = request.GET.get('public_key')
    if public_key == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify a public_key'
        return JsonResponse(response)

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    try:
        response.update(addPublicKey(public_key))

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - secret_key
#
def account_getPublicKeys(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    try:
        response.update(getPublicKey())

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def instance_dashboard(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        response.update({'LoadBalancers':{}})
        response.update({'Instances':{}})
        response.update(getAllVolumes())
        response.update(getAllElasticIPs())
        response.update(getAllSnapshots())
        response.update(getAllImages())

        response['Instances'].update(getAllInstances())
        response['LoadBalancers'].update(getAllLoadBalancers())
        response['LoadBalancers'].update(getAllLoadBalancersV2())

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
# - secret_key
#
def instance_start(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')
    if instance_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an instance_id'
        return JsonResponse(response)

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            response['HTTPStatus'] = 'Unauthorized'
            response['HTTPStatusCode'] = '401'
            response['Message'] = 'Dry run failed'
            response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
# - secret_key
#
def instance_stop(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')
    if instance_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an instance_id'
        return JsonResponse(response)

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            response['HTTPStatus'] = 'Unauthorized'
            response['HTTPStatusCode'] = '401'
            response['Message'] = 'Dry run failed'
            response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
# - secret_key
#
def instance_terminate(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')
    if instance_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an instance_id'
        return JsonResponse(response)

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.terminate_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            response['HTTPStatus'] = 'Unauthorized'
            response['HTTPStatusCode'] = '401'
            response['Message'] = 'Dry run failed'
            response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.terminate_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# TO-DO
# Request:
# - instance_id
# - secret_key
#
def instance_overload(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}
    return JsonResponse(response)

# Request:
# - image_id
# - snapshot_id
# - count
# - secret_key
#
def instance_create(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    new_instances = []

    image_id = request.GET.get('image_id')
    snapshot_id = request.GET.get('snapshot_id')
    number_of_instances = request.GET.get('count')

    secret_key = request.GET.get('secret_key')
    status,results = validate(secret_key)

    if not status:
        return JsonResponse(results)

    try:
        if image_id == None or snapshot_id == None:
            response['HTTPStatus'] = 'Bad request'
            response['HTTPStatusCode'] = '400'
            response['Message'] = 'Please specify image_id and snapshot_id'
            return JsonResponse(response)

        if number_of_instances == None:
            number_of_instances = 1
        else:
            number_of_instances = int(number_of_instances)

        ec2 = boto3.resource('ec2')
        instances_list = ec2.create_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'VirtualName': 'ephemeral0',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'SnapshotId': snapshot_id,
                        'VolumeSize': 10,
                        'VolumeType': 'gp2',
                    },
                },
            ],
            ImageId=image_id,
            InstanceType='t2.micro',
            KeyName='CLE',
            MaxCount=number_of_instances,
            MinCount=1,
            Monitoring={
                'Enabled': False
            },
            SecurityGroups=[
                'Auto-Instance-Security-Group',
            ],
            DisableApiTermination=False,
            EbsOptimized=False,
            InstanceInitiatedShutdownBehavior='stop',
        )

        for instance in instances_list:
            new_instances.append(
                {
                    'instance_id':instance.instance_id,
                }
            )

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    response['instance_ids'] = new_instances
    return JsonResponse(response)

# Request:
#
def instance_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances()
        response.update(instances)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def instance_getCurentInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        instance_id = getInstanceID(

        )
        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances(
            InstanceIds=[
                instance_id,
            ],
        )
        response.update(instances)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
#
def instance_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    try:
        if instance_id == None:
            response['HTTPStatus'] = 'Bad request'
            response['HTTPStatusCode'] = '400'
            response['Message'] = 'Please specify instance_id'
            return JsonResponse(response)

        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances(
            InstanceIds=[
                instance_id,
            ],
        )
        response.update(instances)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def elasticIP_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        results = getAllElasticIPs()
        response.update(results)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
# - allocation_id
#
def elasticIP_associate(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')
    allocation_id = request.GET.get('allocation_id')
    public_ip = ''

    try:
        ec2 = boto3.client('ec2')
        results = ec2.associate_address(
            AllocationId=allocation_id,
            InstanceId=instance_id,
        )

        elastic_ips = getElasticIPs_Assigned()['Elastic_IPs']
        for ip in elastic_ips:
            if ip['InstanceId'] == instance_id:
                public_ip = ip['PublicIp']

        response['Response'] ={
            'instance_id':instance_id,
            'association_id':results['AssociationId'],
            'instance_public_ip':public_ip,
        }

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - namespace
# - name
# - period
#
def cloudwatch_getMetric(request,attempts=0):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    namespace = request.GET.get('namespace')
    name = request.GET.get('name')
    period = request.GET.get('period')

    if namespace == None or name == None or period == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify a namespace, name and period'
        return JsonResponse(response)

    try:
        client = boto3.client('cloudwatch', region_name='ap-southeast-1')

        endTime = datetime.utcnow()
        startTime = (endTime - timedelta(days=1))
        dimension = getDimension(namespace)

        statistics = client.get_metric_statistics(
            Namespace=namespace,
            MetricName=name,
            Dimensions=[dimension],
            StartTime=startTime.isoformat(),
            EndTime=endTime.isoformat(),
            Period=int(period),
            Statistics=[
                'SampleCount','Average','Sum','Minimum','Maximum',
            ],
        )

        response['metric_dimensions'] = [dimension]
        response['metric_metric_name'] = name
        response['metric_statistics'] = statistics

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - namespace
#
def cloudwatch_getAvailableMetrics(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    namespace = request.GET.get('namespace')

    if namespace == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please indicate a namespace'
        return JsonResponse(response)

    try:
        client = boto3.client('cloudwatch')
        dimension = getDimension(namespace)

        results = client.list_metrics(
            Namespace=namespace,
            Dimensions=[dimension],
        )

        response['metric_dimensions'] = [dimension]
        response.update(results)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def loadbalancer_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('elb')
        loadbalancers = client.describe_load_balancers()
        response.update(loadbalancers)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - loadbalancer_name
#
def loadbalancer_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    loadbalancer_name = request.GET.get('loadbalancer_name')

    try:
        if loadbalancer_name == None:
            response['HTTPStatus'] = 'Bad request'
            response['HTTPStatusCode'] = '400'
            response['Message'] = 'Please specify loadbalancer_name. Do take note, this is specifically for Classic Load Balancers.'
            return JsonResponse(response)

        client = boto3.client('elb')
        loadbalancers = client.describe_load_balancers(
            LoadBalancerNames=[
                loadbalancer_name,
            ],
        )
        response.update(loadbalancers)

    except Exception as e:
        # traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def loadbalancerV2_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('elbv2')
        loadbalancers = client.describe_load_balancers()
        response.update(loadbalancers)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - loadbalancer_arn
#
def loadbalancerV2_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    loadbalancer_arn = request.GET.get('loadbalancer_arn')

    try:
        if loadbalancer_arn == None:
            response['HTTPStatus'] = 'Bad request'
            response['HTTPStatusCode'] = '400'
            response['Message'] = 'Please specify loadbalancer_arn. Do take note, this is for Application and Network Load Balancers.'
            return JsonResponse(response)

        client = boto3.client('elbv2')
        loadbalancers = client.describe_load_balancers(
            LoadBalancerArns=[
                loadbalancer_arn,
            ],
        )
        response.update(loadbalancers)

    except Exception as e:
        # traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def volume_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('ec2')
        volumes = client.describe_volumes()
        response.update(volumes)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - volume_id
#
def volume_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    volume_id = request.GET.get('volume_id')

    if volume_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify volume_id'
        return JsonResponse(response)

    try:
        client = boto3.client('ec2')
        volumes = client.describe_volumes(
            VolumeIds=[
                volume_id,
            ],
        )
        response.update(volumes)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def snapshot_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    owner_id = getOwnerID()

    try:
        client = boto3.client('ec2')
        snapshots = client.describe_snapshots(
            OwnerIds=[
                owner_id,
            ],
        )
        response.update(snapshots)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - snapshot_id
#
def snapshot_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    owner_id = getOwnerID()

    snapshot_id = request.GET.get('snapshot_id')
    if snapshot_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify a snapshot_id'
        JsonResponse(response)

    try:
        client = boto3.client('ec2')
        response.update(
            client.describe_snapshots(
                OwnerIds=[
                    owner_id,
                ],
                SnapshotIds=[
                    snapshot_id,
                ]
            )
        )

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def image_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    owner_id = getOwnerID()

    try:
        client = boto3.client('ec2')
        images = client.describe_images(
            Owners=[
                owner_id,
            ],
        )
        response.update(images)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - image_id
#
def image_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    owner_id = getOwnerID()

    image_id = request.GET.get('image_id')
    if image_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an image_id'
        JsonResponse(response)

    try:
        client = boto3.client('ec2')
        response.update(
            client.describe_images(
                Owners=[
                    owner_id,
                ],
                ImageIds=[
                    image_id,
                ]
            )
        )

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

def send_signal(requests):
    import requests as req
    try:
        url = "http://52.77.157.29:8999/event/recovery/?secret_key=m0nKEY&ip=" + PUBLIC_IP
        print(url)
        response = req.get(url)
        #jsonObj = json.loads(response.content.decode())
    except:
        pass