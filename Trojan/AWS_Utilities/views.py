import os
import boto3
import traceback
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.aws_utils import *
from botocore.exceptions import ClientError

# Request:
#
def test(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}
    return JsonResponse(response)

# Request:
#
def account_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('sts')
        account = client.get_caller_identity()

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    response['User'] = account
    response['User'].update(getCredentials())
    return JsonResponse(response)

# Request:
# - public_key
#
def account_addPublicKey(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    public_key = request.GET.get('public_key')

    try:
        if public_key == None:
            response['HTTPStatus'] = 'Bad request'
            response['HTTPStatusCode'] = '400'
            response['Message'] = 'Please specify an public_key'
            return JsonResponse(response)

        response.update(addPublicKey(public_key))

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def account_getPublicKeys(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

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
#
def instance_start(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    if instance_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an instance_id'
        return JsonResponse(response)

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
#
def instance_stop(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    if instance_id == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Message'] = 'Please specify an instance_id'
        return JsonResponse(response)

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
