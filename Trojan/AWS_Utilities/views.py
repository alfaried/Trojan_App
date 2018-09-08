import boto3
import traceback
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.aws_utils import *
from botocore.exceptions import ClientError


def test(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}
    return JsonResponse(response)

# Request:
#
def instance_stop(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = getInstanceID()
    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except UnauthorizedOperation as e:
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
def instance_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = getInstanceID()
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(instance_id)

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
    endTime = datetime.utcnow()
    startTime = (endTime - timedelta(days=2))

    try:
        client = boto3.client('cloudwatch', region_name='ap-southeast-1')

        dimensions_name = 'InstanceId'
        value = getInstanceID()

        statistics = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=name,
            Dimensions=[
                {
                    'Name':dimensions_name,
                    'Value':value
                },
            ],
            StartTime=startTime.isoformat(),
            EndTime=endTime.isoformat(),
            Period=int(period),
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

# Request:
# - namespace
#
def cloudwatch_getAvailableMetrics(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    namespace = request.GET.get('namespace')

    dimensions_name = 'InstanceId'
    value = getInstanceID()

    if 'EBS' in namespace:
        dimensions_name = 'VolumeId'
        value = getVolumeID()

    # to-do:
    # Configure to take in more parameters instead of just EC2 and EBS

    client = boto3.client('cloudwatch', region_name='ap-southeast-1')
    results = client.list_metrics(
        Namespace=namespace,
        Dimensions=[
            {
                'Name':dimensions_name,
                'Value':value
            },
        ],
    )

    response['Namespace'] = namespace
    response['Dimensions_Name'] = dimensions_name
    response.update(results)

    return JsonResponse(response)
