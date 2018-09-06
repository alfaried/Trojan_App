import boto3
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.aws_utils import *
from botocore.exceptions import ClientError

def test(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}
    return JsonResponse(response)

def killInstance(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}

    instance_id = getInstanceID()
    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        response['HTTPStatus'] = 'Unauthorized'
        response['HTTPStatusCode'] = '401'
        response['Message'] = 'Dry run failed'
        response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except ClientError as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

def getInstanceInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}

    instance_id = getCurrentInstanceID()
    instance = getInstance(instance_id)

    response['instance_id'] = instance.instance_id
    response['instance_public_ip'] = instance.public_ip_address
    response['instance_public_dns_name'] = instance.public_dns_name
    response['instance_private_ip_address'] = instance.private_ip_address
    response['instance_private_dns_name'] = instance.private_dns_name
    response['instance_type'] = instance.instance_type
    response['instance_kernel_id'] = instance.kernel_id
    response['instance_security_groups'] = instance.security_groups
    response['instance_state'] = instance.state
    response['instance_subnet_id'] = instance.subnet_id
    response['instance_tags'] = instance.tags
    response['instance_vpc_id'] = instance.vpc_id
    response['instance_launch_time'] = instance.launch_time

    return JsonResponse(response)

def getCloudWatchInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}

    namespace = request.GET.get('namespace')
    name = request.GET.get('name')

    try:
        client = boto3.resource('cloudwatch')
        metric = cloudwatch.Metric(namespace,name)

        response['metric_dimensions'] = metric.dimensions
        response['metric_metric_name'] = metric.metric_name
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)
