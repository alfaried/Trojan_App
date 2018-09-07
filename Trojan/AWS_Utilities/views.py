import boto3
import traceback
from datetime import datetime, timedelta
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

    instance_id = getCurrentInstanceID()
    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except Exception as e:
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

def getInstanceInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}

    instance_id = getCurrentInstanceID()
    instance = getInstance(instance_id)

    try:
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

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

def getCloudWatchMetricInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':'200'}

    namespace = request.GET.get('namespace')
    name = request.GET.get('name')

    try:
        cloudwatch = boto3.resource('cloudwatch')
        metric = cloudwatch.Metric(namespace,name)

        dimensions = metric.dimensions
        startTime = datetime(2018, 8, 31)
        endTime = startTime + timedelta(hours=3)
        period = 300

        statistics = metric.get_statistics(
            Dimensions=dimensions,
            StartTime=startTime,
            EndTime=endTime,
            Period=period,
            Statistics=[
                'SampleCount','Average','Sum','Minimum','Maximum',
            ],
        )

        response['metric_dimensions'] = dimensions
        response['metric_metric_name'] = metric.metric_name
        response['metric_statistics'] = statistics

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)
